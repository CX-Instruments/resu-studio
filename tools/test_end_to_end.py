"""End-to-end regression for the whole branch: steps 1 to 4b working together.

One fictional person, the skill installed inside a project the way `npx skills add` does,
no host data folder set, a real git repository. Runs the chain an assistant would run:
choose the folder, start two jobs, score, build both Studios, print a PDF, check, Resu Desk,
a Desk change applied back, and then proves nothing private landed anywhere else.

    python3 tools/test_end_to_end.py     prints "N of N checks passed", exit 1 on any fail

Needs git, and a Chromium-family browser for the PDF (CV_BROWSER).
"""
import glob, json, os, re, shutil, subprocess, sys, tempfile
from urllib.parse import unquote

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCR = os.path.join(tempfile.gettempdir(), "resu-test-end-to-end")
HOME = os.path.join(SCR, "home")
PROJECT = os.path.join(SCR, "Career")
SKILL = os.path.join(PROJECT, ".agents", "skills", "resu-studio")
DATA = os.path.join(PROJECT, "Resu - CV Builder")
DOCS = os.path.join(DATA, "4 Finished documents")
ENV = {k: v for k, v in os.environ.items() if k not in ("CLAUDE_PLUGIN_DATA", "PLUGIN_DATA", "RESU_STUDIO_CONFIG")}
ENV.update(HOME=HOME, USERPROFILE=HOME, RESU_WORKSPACE=PROJECT)
browser = os.environ.get("CV_BROWSER") or next(iter(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome")), "")
if browser:
    ENV["CV_BROWSER"] = browser
steps = []


def short(t):
    t = t.replace(PROJECT, "D:/Career").replace(HOME, "~")
    return t.replace("\\", "/") if os.sep == "\\" else t


def run(*args):
    p = subprocess.run([sys.executable] + list(args), cwd=SKILL, env=ENV, capture_output=True,
                       text=True, encoding="utf-8")
    return p.returncode, short((p.stdout + p.stderr).rstrip())


def step(title, cmd, checks):
    code, out = run(*cmd)
    res = {"title": title, "why": "", "cmd": short("python3 " + " ".join('"%s"' % c if " " in c else c for c in cmd)),
           "code": code, "out": out, "checks": []}
    for label, fn in checks:
        try:
            ok = bool(fn(code, out))
        except Exception as e:                                  # noqa: BLE001
            ok, label = False, label + " (error: %s)" % e
        res["checks"].append([label, ok])
    steps.append(res)
    return code, out


def w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


shutil.rmtree(SCR, ignore_errors=True)
shutil.copytree(os.path.join(REPO, "skills", "resu-studio"), SKILL,
                ignore=shutil.ignore_patterns("__pycache__", "data", "data-location.txt"))
os.makedirs(HOME)
w(os.path.join(PROJECT, "notes.md"), "Project notes.\n")
subprocess.run(["git", "init", "-q"], cwd=PROJECT, env=ENV)

step("1. Fresh install, nothing chosen", ["scripts/paths.py", "--status"],
     [("uses workspace default", lambda c, o: "current workspace default" in o)])
step("2. Choose the project folder", ["scripts/paths.py", "--choose", "project"],
     [("exit 0", lambda c, o: c == 0), ("made the folder", lambda c, o: os.path.isdir(os.path.join(DATA, "3 Jobs")))])

code, about = run("scripts/paths.py", "--about")
CV = os.path.join(DATA, "1 About me", "Alex Morgan CV.md")
shutil.copy(os.path.join(REPO, "docs", "review", "sample-cv.md"), CV)
steps.append({"title": "3. CV and facts go where paths.py says", "why": "", "cmd": "python3 scripts/paths.py --about",
              "code": code, "out": about, "checks": [["--about names 1 About me in the project", about.endswith("D:/Career/Resu - CV Builder/1 About me")]]})

step("4. Start job one", ["scripts/jobs.py", "new", "--role", "Operations Coordinator", "--employer", "Northside Community Care", "--closes", "2026-10-03"],
     [("exit 0", lambda c, o: c == 0), ("folder in 3 Jobs", lambda c, o: "D:/Career/Resu - CV Builder/3 Jobs/northside" in o)])
step("5. Start job two", ["scripts/jobs.py", "new", "--role", "Venue Manager", "--employer", "Riverbend Events"],
     [("exit 0", lambda c, o: c == 0)])
A = [n for n in os.listdir(os.path.join(DATA, "3 Jobs")) if n.startswith("northside")][0]
B = [n for n in os.listdir(os.path.join(DATA, "3 Jobs")) if n.startswith("riverbend")][0]
w(os.path.join(DATA, "3 Jobs", A, "facts.md"), "# Facts\n\n```\nid: fact-roster\ntext: Rostered 35 casual staff\n```\n")
code, jdir = run("scripts/paths.py", "--job", "northside")
SC = ("---\ndepth: essentials\ncounts:\n  asks_total: 2\n  must: 2\n  you_have: 2\n  a_reader_would_find: %d\n  unscored: 0\n---\n\n"
      "| Ask | Necessity | State | Evidence | Note |\n|---|---|---|---|---|\n"
      "| Rostering | must | page | Built and maintained weekly rosters | |\n| Community services | must | %s | | |\n")
w(os.path.join(DATA, "3 Jobs", A, "scorecard.md"), SC % (1, "missing"))
w(os.path.join(DATA, "3 Jobs", B, "scorecard.md"), SC % (2, "page"))

step("6. Record the first score", ["scripts/jobs.py", "score", "northside", "--scorecard", os.path.join(DATA, "3 Jobs", A, "scorecard.md"), "--as", "before"],
     [("exit 0", lambda c, o: c == 0), ("1 of 2 found", lambda c, o: "1/2 found" in o)])
step("7. Studio for job one", ["scripts/build_studio.py", "--cv", CV, "--job", "northside", "--scorecard", os.path.join(DATA, "3 Jobs", A, "scorecard.md")],
     [("exit 0", lambda c, o: c == 0),
      ("in 4 Finished documents, job one's folder", lambda c, o: "D:/Career/Resu - CV Builder/4 Finished documents/Northside Community Care - Operations Coordinator/" in o),
      ("Desk updated", lambda c, o: "desk   : D:/Career/Resu - CV Builder/4 Finished documents/Resu Desk.html" in o)])
step("8. Studio for job two", ["scripts/build_studio.py", "--cv", CV, "--job", "riverbend", "--scorecard", os.path.join(DATA, "3 Jobs", B, "scorecard.md")],
     [("exit 0", lambda c, o: c == 0), ("its own store", lambda c, o: "cvwb:venue-manager-riverbend-events" in o)])
step("9. PDF for job one", ["scripts/render_cv.py", CV, "--job", "northside", "--pdf"],
     [("exit 0", lambda c, o: c == 0),
      ("PDF in job one's folder", lambda c, o: glob.glob(os.path.join(DOCS, "Northside Community Care - Operations Coordinator", "*CV.pdf")))])
step("10. check.py on job one", ["scripts/check.py", "--job", "northside"],
     [("does not fall back to shared facts", lambda c, o: "facts from" not in o),
      ("counts the fact", lambda c, o: "facts: 1" in o)])
step("11. documents.py names both jobs", ["scripts/documents.py"],
     [("job one", lambda c, o: "[job %s]" % A in o), ("job two", lambda c, o: "[job %s]" % B in o)])

DESK = os.path.join(DOCS, "Resu Desk.html")
data = json.loads(re.search(r"^const DESK = (\{.*\});$", open(DESK, encoding="utf-8").read(), re.M).group(1).replace("<\\/", "</"))
w(os.path.join(SCR, "desk-updates.json"), json.dumps({"desk": 1, "changes": [{"job": B, "stage": {"from": "Saved", "to": "Applied"}, "note": "Sent today"}]}))
step("12. A Desk change applied back", ["scripts/jobs.py", "apply-desk", os.path.join(SCR, "desk-updates.json")],
     [("exit 0", lambda c, o: c == 0),
      ("job two is Applied", lambda c, o: json.load(open(os.path.join(DATA, "3 Jobs", B, "job.json")))["stage"] == "Applied")])
data = json.loads(re.search(r"^const DESK = (\{.*\});$", open(DESK, encoding="utf-8").read(), re.M).group(1).replace("<\\/", "</"))
steps.append({"title": "13. Resu Desk", "why": "", "cmd": "", "code": None, "out": "", "checks": [
    ["two jobs on it", len(data["jobs"]) == 2],
    ["job one shows Studio and CV PDF", [d["kind"] for d in next(j for j in data["jobs"] if j["id"] == A)["docs"]] == ["studio", "cv"]],
    ["every link opens a real file", all(os.path.isfile(os.path.join(DOCS, unquote(d["href"]))) for j in data["jobs"] for d in j["docs"])],
    ["the rebuilt Desk shows job two Applied", next(j for j in data["jobs"] if j["id"] == B)["stage"] == "Applied"]]})

gs = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=PROJECT, env=ENV, capture_output=True, text=True).stdout
# The browser that printed the PDF keeps its own cache in the home folder. That is Chrome's, not ours.
home_files = [os.path.relpath(os.path.join(d, f), HOME) for d, _, fs in os.walk(HOME) for f in fs
              if not os.path.relpath(d, HOME).split(os.sep)[0] in (".cache", ".config", ".pki", ".local")]
leaks = [os.path.join(d, f) for d, _, fs in os.walk(SKILL) for f in fs
         if not f.endswith((".pyc",)) and "Alex Morgan" in open(os.path.join(d, f), "rb").read().decode("utf-8", "ignore")]
steps.append({"title": "14. Nothing private anywhere else", "why": "",
              "cmd": "", "code": None,
              "out": "git status, not counting the skill's own files:\n%s\n\nfiles in the home folder: %s"
                     % ("\n".join(l for l in gs.splitlines() if ".agents/" not in l), ", ".join(home_files)),
              "checks": [["git sees nothing in Resu - CV Builder", "Resu - CV Builder" not in gs],
                         ["no application settings or data written in the home folder", home_files == []],
                         ["no personal detail was written inside the skill folder", not leaks]]})

json.dump({"steps": steps}, open(os.path.join(SCR, "results.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
total = sum(len(s["checks"]) for s in steps)
passed = sum(ok for s in steps for _, ok in s["checks"])
print("%d of %d checks passed" % (passed, total))
for s in steps:
    for label, ok in s["checks"]:
        if not ok:
            print("FAIL", s["title"], "|", label, "\n", s["out"][-800:])
sys.exit(0 if passed == total else 1)
