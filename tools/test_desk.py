"""Test run for step 4 of docs/multi-job-plan.md: Resu Desk and jobs.py apply-desk.

Five fictional applications for the fictional person in docs/review/sample-cv.md, at
different stages. Builds real Studios and a real PDF, builds the Desk, then opens it in
a real browser, changes things on the page the way a person would, saves the desk file,
applies it, and checks the records and the rebuilt page.

    python3 tools/test_desk.py      prints "N of N checks passed", exit 1 on any fail

Needs a Chromium-family browser for the PDF (CV_BROWSER) and Playwright for Python for
the page checks (pip install playwright). Without either, those checks fail by name.
Screenshots are written to <temp>/resu-test-desk/shots.
"""
import datetime, glob, json, os, pathlib, re, shutil, subprocess, sys, tempfile
from urllib.parse import unquote

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(REPO, "skills", "resu-studio")
SCR = os.path.join(tempfile.gettempdir(), "resu-test-desk")
DATA = os.path.join(SCR, ".resu-studio")
DOCS = os.path.join(DATA, "4 Finished documents")
DESK = os.path.join(DOCS, "Resu Desk.html")
SHOTS = os.path.join(SCR, "shots")
ENV = dict(os.environ, CLAUDE_PLUGIN_DATA=DATA, RESU_STUDIO_CONFIG=os.path.join(SCR, "config"))
steps = []


def day(n):
    return (datetime.date.today() + datetime.timedelta(days=n)).isoformat()


def _slash(t):
    """Output with / between folders on every system, so one check reads Windows and Linux alike."""
    return t.replace("\\", "/") if os.sep == "\\" else t


def run(*args, env=None):
    p = subprocess.run([sys.executable] + list(args), cwd=SKILL, env=env or ENV,
                       capture_output=True, text=True, encoding="utf-8")
    return p.returncode, _slash((p.stdout + p.stderr).replace(DATA, "~/.resu-studio").rstrip())


def step(title, why, cmd=None, checks=(), shot=None, env=None):
    code, out = run(*cmd, env=env) if cmd else (None, "")
    res = {"title": title, "why": why, "code": code, "out": out, "checks": [], "shot": shot,
           "cmd": ("python3 " + " ".join('"%s"' % c if " " in c else c for c in cmd))
                  .replace(DATA, "~/.resu-studio").replace(SCR, "<temp>") if cmd else ""}
    for label, fn in checks:
        try:
            ok = bool(fn(code, out))
        except Exception as e:                                  # noqa: BLE001
            ok, label = False, label + " (error: %s)" % e
        res["checks"].append([label, ok])
    steps.append(res)
    return code, out


def job(jid):
    return json.load(open(os.path.join(DATA, "3 Jobs", jid, "job.json"), encoding="utf-8"))


def desk_data(path=DESK):
    m = re.search(r"^const DESK = (\{.*\});$", open(path, encoding="utf-8").read(), re.M)
    return json.loads(m.group(1).replace("<\\/", "</"))


def w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


SCORE = "---\ndepth: essentials\ncounts:\n  asks_total: %d\n  must: %d\n  you_have: %d\n  a_reader_would_find: %d\n  unscored: 0\n---\n"

# ---------------------------------------------------------------- five fictional jobs
shutil.rmtree(SCR, ignore_errors=True)
os.makedirs(SHOTS)
w(os.path.join(DATA, "2 My record", "facts.md"), "# Facts\n")
CV = os.path.join(DATA, "1 About me", "Alex Morgan CV.md")
os.makedirs(os.path.dirname(CV))
shutil.copy(os.path.join(REPO, "docs", "review", "sample-cv.md"), CV)

A = "northside-community-care-operations-coordinator-" + day(0)[:7]
B = "riverbend-events-venue-manager-" + day(0)[:7]
C = "coastal-parks-trust-events-officer-" + day(0)[:7]
D = "old-mill-foods-reporting-lead-" + day(0)[:7]
E = "harbour-health-rostering-officer-" + day(0)[:7]
J = "scripts/jobs.py"
for args in (["new", "--role", "Operations Coordinator", "--employer", "Northside Community Care", "--closes", day(3)],
             ["new", "--role", "Venue Manager", "--employer", "Riverbend Events", "--closes", day(-5)],
             ["new", "--role", "Events Officer", "--employer", "Coastal Parks Trust", "--closes", day(20),
              "--link", "https://example.com/jobs/events-officer"],
             ["new", "--role", "Reporting Lead", "--employer", "Old Mill Foods", "--closes", day(-30)],
             ["new", "--role", "Rostering Officer", "--employer", "Harbour Health", "--closes", day(-1)],
             ["stage", "northside", "Tailoring"], ["stage", "riverbend", "Applied"],
             ["stage", "old-mill", "Rejected"], ["stage", "harbour", "Scoring"],
             ["note", "riverbend", "Sent through their portal, reference RE-2291"],
             ["note", "old-mill", "Email said the role went to an internal applicant"]):
    run(J, *args)
w(os.path.join(SCR, "before.md"), SCORE % (3, 3, 3, 2))
w(os.path.join(SCR, "after.md"), SCORE % (3, 3, 3, 3))
run(J, "score", "northside", "--scorecard", os.path.join(SCR, "before.md"), "--as", "before")
run(J, "score", "northside", "--scorecard", os.path.join(SCR, "after.md"), "--as", "after")
run(J, "score", "harbour", "--scorecard", os.path.join(SCR, "before.md"), "--as", "before")

step("1. Five jobs, and the Desk already exists",
     "Every jobs.py command that changed a record rebuilt the Desk on its own. Nobody ran build_desk.py yet.",
     [J, "list"],
     checks=[("all five jobs listed", lambda c, o: all(x in o for x in (A, B, C, D, E))),
             ("Resu Desk.html was written by the jobs.py commands", lambda c, o: os.path.isfile(DESK)),
             ("the Desk holds all five", lambda c, o: len(desk_data()["jobs"]) == 5)])

step("2. Build the Northside studio: the Desk updates",
     "build_studio.py rebuilds the Desk after it writes, and says where.",
     ["scripts/build_studio.py", "--cv", CV, "--job", "northside"],
     checks=[("exit code 0", lambda c, o: c == 0),
             ("names the Desk it updated", lambda c, o: "desk   : ~/.resu-studio/4 Finished documents/Resu Desk.html" in o),
             ("the Desk now lists the Northside studio",
              lambda c, o: [d["kind"] for d in next(j for j in desk_data()["jobs"] if j["id"] == A)["docs"]] == ["studio"])])
run("scripts/build_studio.py", "--cv", CV, "--job", "riverbend")

browser = os.environ.get("CV_BROWSER") or next(iter(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome")), "")
if browser:
    ENV["CV_BROWSER"] = browser
step("3. Print the Northside CV: the Desk updates again", "",
     ["scripts/render_cv.py", CV, "--job", "northside", "--pdf"],
     checks=[("exit code 0", lambda c, o: c == 0),
             ("the Desk lists the Studio, then the CV PDF",
              lambda c, o: [d["kind"] for d in next(j for j in desk_data()["jobs"] if j["id"] == A)["docs"]] == ["studio", "cv"])])

step("4. build_desk.py on its own", "", ["scripts/build_desk.py"],
     checks=[("exit code 0", lambda c, o: c == 0),
             ("says 5 jobs", lambda c, o: "5 jobs on it" in o),
             ("every link on the Desk opens a real file", lambda c, o: all(
                 os.path.isfile(os.path.join(DOCS, unquote(d["href"])))
                 for j in desk_data()["jobs"] for d in j["docs"])),
             ("the folder's path is not written into the page",
              lambda c, o: DATA not in open(DESK, encoding="utf-8").read()),
             ("no network: no http link in the page except the job ad",
              lambda c, o: set(re.findall(r'https?://[^"\s<>)]+', open(DESK, encoding="utf-8").read()))
              <= {"https://example.com/jobs/events-officer"})])

# ---------------------------------------------------------------- the page, in a real browser
try:
    from playwright.sync_api import sync_playwright
    HAVE_PW = True
except ImportError:
    HAVE_PW = False

page_facts = {}
if HAVE_PW:
    with sync_playwright() as p:
        b = p.chromium.launch(**({"executable_path": os.environ["CV_BROWSER"]}
                                if os.environ.get("CV_BROWSER") else {}))
        ctx = b.new_context(viewport={"width": 1280, "height": 900}, accept_downloads=True)
        pg = ctx.new_page()
        errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.goto("file://" + DESK)
        pg.wait_for_timeout(400)
        pg.screenshot(path=os.path.join(SHOTS, "desk-light.png"), full_page=True)
        rowtext = lambda jid: pg.locator('[data-job="%s"]' % jid).first.inner_text()
        page_facts.update({
            "errors": list(errors),
            "open_rows": pg.locator("#open .job").count(),
            "closed_sum": pg.locator("#closedSum").inner_text(),
            "A": rowtext(A), "B": rowtext(B), "E": rowtext(E),
            "chips": pg.locator("#filters").inner_text(),
        })
        # The Studio link opens in a new tab and leaves the Desk where it was.
        page_facts["embedded_hidden"] = pg.locator("#embedded").is_hidden()
        with ctx.expect_page() as newtab:
            pg.locator('[data-job="%s"] .docs a.cta' % A).first.click()
        studio = newtab.value
        studio.wait_for_load_state()
        page_facts["studio_title"] = studio.title()
        page_facts["desk_still_open"] = pg.url.endswith("Resu%20Desk.html") or pg.url.endswith("Resu Desk.html")
        page_facts["doc_links_new_tab"] = pg.locator(".docs a.cta").evaluate_all("as => as.length > 0 && as.every(a => a.target === '_blank' && a.rel === 'noopener')")
        studio.close()
        # Shown inside another page, as an editor preview does, the Desk says to open it in the browser.
        wrapper = os.path.join(SCR, "preview.html")
        with open(wrapper, "w", encoding="utf-8") as fh:
            fh.write('<iframe src="%s" style="width:1200px;height:800px"></iframe>' % pathlib.Path(DESK).as_uri())
        fr = ctx.new_page()
        fr.goto(pathlib.Path(wrapper).as_uri())
        fr.wait_for_timeout(800)
        fr.screenshot(path=os.path.join(SHOTS, "desk-in-preview.png"))
        inner = fr.frames[1] if len(fr.frames) > 1 else None
        page_facts["embedded_shown"] = bool(inner) and inner.locator("#embedded").is_visible()
        fr.close()

        dark = b.new_context(viewport={"width": 1280, "height": 900}, color_scheme="dark")
        dp = dark.new_page(); dp.goto("file://" + DESK); dp.wait_for_timeout(300)
        dp.screenshot(path=os.path.join(SHOTS, "desk-dark.png"), full_page=True)
        page_facts["dark_bg"] = dp.evaluate("getComputedStyle(document.body).backgroundColor")
        dark.close()

        phone = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2)
        pp = phone.new_page(); pp.goto("file://" + DESK); pp.wait_for_timeout(300)
        pp.screenshot(path=os.path.join(SHOTS, "desk-phone.png"), full_page=False)
        page_facts["phone_overflow"] = pp.evaluate("document.documentElement.scrollWidth > window.innerWidth")
        phone.close()

        # A person's changes: Riverbend moves on to Interview with a note, Coastal's date moves.
        pg.locator('[data-job="%s"] details.update > summary' % B).click()
        pg.select_option('[data-job="%s"] select.stage' % B, "Interview")
        pg.fill('[data-job="%s"] textarea.note' % B, "Interview on Thursday at 10, with the venue director")
        pg.locator('[data-job="%s"] textarea.note' % B).dispatch_event("change")
        pg.locator('[data-job="%s"] details.update > summary' % C).click()
        pg.fill('[data-job="%s"] input.date' % C, day(25))
        pg.locator('[data-job="%s"] input.date' % C).dispatch_event("change")
        pg.click("#handBtn")
        pg.wait_for_timeout(200)
        page_facts["hand"] = pg.locator("#handText").input_value()
        page_facts["tray"] = pg.locator("#changesMsg").inner_text()
        pg.screenshot(path=os.path.join(SHOTS, "desk-changed.png"), full_page=False)
        page_facts["drawer_shot"] = True
        with pg.expect_download() as dl:
            pg.click("#saveBtn2")
        dl.value.save_as(os.path.join(SCR, "desk-updates.json"))
        w(os.path.join(SCR, "pasted.txt"), page_facts["hand"])

        # Meanwhile the assistant changes Coastal's closing date in the chat.
        run(J, "set", "coastal", "closes", day(22))
        page_facts["apply"] = run(J, "apply-desk", os.path.join(SCR, "desk-updates.json"))

        pg.goto("file://" + DESK)
        pg.wait_for_timeout(400)
        page_facts["after_tray"] = pg.locator("#changesMsg").inner_text()
        page_facts["after_tray_hidden"] = pg.locator("#barHand").is_hidden()
        page_facts["B_changed"] = "changed" in (pg.locator('[data-job="%s"]' % B).first.get_attribute("class") or "")
        page_facts["C_changed"] = "changed" in (pg.locator('[data-job="%s"]' % C).first.get_attribute("class") or "")
        page_facts["B_after"] = pg.locator('[data-job="%s"]' % B).first.inner_text()
        page_facts["C_after"] = pg.locator('[data-job="%s"]' % C).first.inner_text()
        pg.screenshot(path=os.path.join(SHOTS, "desk-after-apply.png"), full_page=True)
        page_facts["errors"] += errors
        b.close()

no_pw = "Playwright for Python is not installed, so the page was not opened"
step("5. The Desk in a browser",
     "Open applications first with the next thing to do, closing dates flagged, the rejected one folded away.",
     shot="desk-light.png",
     checks=[(no_pw, lambda c, o: HAVE_PW)] if not HAVE_PW else [
         ("no script errors on the page", lambda c, o: not page_facts["errors"]),
         ("4 open rows", lambda c, o: page_facts["open_rows"] == 4),
         ("the rejected job is folded away as Closed (1)", lambda c, o: page_facts["closed_sum"].lower() == "closed (1)"),
         ("Northside says closes in 3 days", lambda c, o: "closes in 3 days" in page_facts["A"].lower()),
         ("Harbour Health says closed 1 day ago", lambda c, o: "closed 1 day ago" in page_facts["E"].lower()),
         ("Riverbend, already applied, has no closing flag", lambda c, o: "closes in" not in page_facts["B"].lower() and "ago" not in page_facts["B"].lower()),
         ("Northside shows the score moving 2 to 3 of 3", lambda c, o: "2 → 3" in page_facts["A"] and "of 3" in page_facts["A"]),
         ("the Studio link opens the Northside Studio", lambda c, o: page_facts["studio_title"].startswith("Resu Studio - Operations Coordinator")),
         ("it opens in a new tab and the Desk stays open", lambda c, o: page_facts["desk_still_open"]),
         ("every document button opens a new tab", lambda c, o: page_facts["doc_links_new_tab"]),
         ("no preview notice in a real browser tab", lambda c, o: page_facts["embedded_hidden"]),
         ("inside a preview frame, the Desk says to open it in the browser", lambda c, o: page_facts["embedded_shown"])])

step("6. Dark mode and phone width", "", shot="desk-dark.png",
     checks=[(no_pw, lambda c, o: HAVE_PW)] if not HAVE_PW else [
         ("dark mode uses the Studio's dark table colour", lambda c, o: page_facts["dark_bg"] == "rgb(20, 23, 28)"),
         ("nothing wider than a 390px phone", lambda c, o: not page_facts["phone_overflow"])])

step("7. Changing things on the page",
     "Riverbend moved to Interview with a note, Coastal Parks' closing date moved. Nothing is written yet.",
     shot="desk-changed.png",
     checks=[(no_pw, lambda c, o: HAVE_PW)] if not HAVE_PW else [
         ("the tray says 2 applications changed", lambda c, o: "changed 2 applications" in page_facts["tray"]),
         ("hand to AI names the stage change", lambda c, o: "stage: Applied to Interview" in page_facts["hand"]),
         ("hand to AI carries the JSON", lambda c, o: "```json" in page_facts["hand"]),
         ("the saved file carries what each change replaced", lambda c, o: any(
             ch.get("stage") == {"from": "Applied", "to": "Interview"}
             for ch in json.load(open(os.path.join(SCR, "desk-updates.json")))["changes"]))])

if HAVE_PW:
    ac, ao = page_facts["apply"]
    steps.append({"title": "8. apply-desk, after the record moved on",
                  "why": "Before applying, the assistant set Coastal Parks' closing date in the chat. "
                         "The Desk's older idea of that date is refused. Riverbend's changes go in.",
                  "code": ac, "out": ao, "shot": None,
                  "cmd": "python3 scripts/jobs.py apply-desk <temp>/desk-updates.json", "checks": []})
    s8 = steps[-1]
    for label, ok in (("exit code 4, because one change was refused", ac == 4),
                      ("Riverbend is now at Interview", job(B)["stage"] == "Interview"),
                      ("the note is on Riverbend", job(B)["notes"][-1]["text"].startswith("Interview on Thursday")),
                      ("Coastal Parks keeps the date the assistant set", job(C)["closes"] == day(22)),
                      ("the refusal names Coastal Parks and both dates", "REFUSED" in ao and "Coastal Parks" in ao and day(22) in ao)):
        s8["checks"].append([label, ok])
else:
    step("8. apply-desk", "", checks=[(no_pw, lambda c, o: False)])

step("9. The rebuilt Desk, opened again in the same browser",
     "Riverbend's changes are in the records now, so the page drops them. The refused one is still waiting.",
     shot="desk-after-apply.png",
     checks=[(no_pw, lambda c, o: HAVE_PW)] if not HAVE_PW else [
         ("Riverbend shows Interview and is not marked changed", lambda c, o: not page_facts["B_changed"] and "Interview" in page_facts["B_after"]),
         ("Coastal Parks is still marked changed", lambda c, o: page_facts["C_changed"]),
         ("Coastal Parks' card says the records now hold a different date", lambda c, o: "out of date" in page_facts["C_after"].lower() and "your records now say the closing date is" in page_facts["C_after"].lower()),
         ("the tray now says 1 application", lambda c, o: "changed 1 application" in page_facts["after_tray"])])

if HAVE_PW:
    step("10. The pasted hand-to-AI text works too",
         "An assistant may save the whole paste instead of just the JSON. --dry-run changes nothing.",
         [J, "apply-desk", os.path.join(SCR, "pasted.txt"), "--dry-run"],
         checks=[("reads the JSON out of the pasted text", lambda c, o: "would write" in o),
                 ("Riverbend's changes are seen as already done", lambda c, o: "no change: Venue Manager at Riverbend Events: already at Interview" in o),
                 ("says nothing was changed", lambda c, o: "nothing was changed" in o)])

run(J, "note", "harbour", "Recruiter said: </script><b>not bold</b>")
step("11. A note that looks like code cannot break the page",
     "The note is stored and drawn as text.", ["scripts/build_desk.py"],
     checks=[("exit code 0", lambda c, o: c == 0),
             ("the note survives the round trip exactly", lambda c, o: any(
                 n["text"] == "Recruiter said: </script><b>not bold</b>"
                 for n in next(j for j in desk_data()["jobs"] if j["id"] == E)["notes"])),
             ("the page holds no raw </script> from the note", lambda c, o: "</script><b>" not in open(DESK, encoding="utf-8").read())])

os.remove(DESK)
os.makedirs(DESK)          # a folder where the Desk should go: it cannot be written
step("12. A Desk that cannot be written does not fail the studio",
     "A folder was put where Resu Desk.html goes.",
     ["scripts/build_studio.py", "--cv", CV, "--job", "riverbend"],
     checks=[("exit code 0", lambda c, o: c == 0),
             ("says in one line the Desk was not updated", lambda c, o: o.count("Resu Desk was not updated") == 1),
             ("the studio was still written", lambda c, o: "wrote ~/.resu-studio/4 Finished documents/Riverbend Events - Venue Manager/" in o),
             ("no temporary file left behind", lambda c, o: not os.path.exists(DESK + ".tmp"))])
os.rmdir(DESK)

EMPTY = dict(os.environ, CLAUDE_PLUGIN_DATA=os.path.join(SCR, "empty"), RESU_STUDIO_CONFIG=os.path.join(SCR, "config"))
step("13. A person with no jobs yet", "", ["scripts/build_desk.py"], env=EMPTY,
     checks=[("exit code 0", lambda c, o: c == 0),
             ("0 jobs on it", lambda c, o: "0 jobs on it" in o)])

json.dump({"steps": steps, "shots": SHOTS}, open(os.path.join(SCR, "results.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
total = sum(len(s["checks"]) for s in steps)
passed = sum(ok for s in steps for _, ok in s["checks"])
print("%d of %d checks passed" % (passed, total))
print("screenshots: %s" % SHOTS)
for s in steps:
    for label, ok in s["checks"]:
        if not ok:
            print("FAIL", s["title"], "|", label, "\n", (s["out"] or "")[-600:])
if HAVE_PW and page_facts.get("errors"):
    print("page errors:", page_facts["errors"])
sys.exit(0 if passed == total else 1)
