"""Test run for step 3 of docs/multi-job-plan.md: the studio, the PDF and check.py per job.

Uses the fictional CV in docs/review/sample-cv.md and two fictional employers. Runs the
real scripts in a temp folder, with CLAUDE_PLUGIN_DATA pointed at it, and checks where
every file lands and what the ledger records.

    python3 tools/test_jobs_build.py     prints "N of N checks passed", exit 1 on any fail

Printing a PDF needs a Chromium-family browser. Set CV_BROWSER to one if it is not found;
without one the PDF checks are reported as failed, not skipped.
"""
import glob, json, os, re, shutil, subprocess, sys, tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(REPO, "skills", "resu-studio")
SCR = os.path.join(tempfile.gettempdir(), "resu-test-build")
DATA = os.path.join(SCR, ".resu-studio")
ENV = dict(os.environ, CLAUDE_PLUGIN_DATA=DATA, RESU_STUDIO_CONFIG=os.path.join(SCR, "config"))
DOCS = os.path.join(DATA, "4 Finished documents")
steps = []


def run(*args):
    p = subprocess.run([sys.executable] + list(args), cwd=SKILL, env=ENV,
                       capture_output=True, text=True, encoding="utf-8")
    return p.returncode, (p.stdout + p.stderr).replace(DATA, "~/.resu-studio").rstrip()


def tree(root):
    lines = []
    def walk(d, pre):
        names = sorted(os.listdir(d), key=lambda n: (not os.path.isdir(os.path.join(d, n)), n.lower()))
        names = [n for n in names if not n.startswith(".")]
        for i, n in enumerate(names):
            last, full = i == len(names) - 1, os.path.join(d, n)
            lines.append([pre + ("└── " if last else "├── ") + n + ("/" if os.path.isdir(full) else ""),
                          os.path.relpath(full, root)])
            if os.path.isdir(full):
                walk(full, pre + ("    " if last else "│   "))
    walk(root, "")
    return lines


def step(title, why, cmd=None, checks=(), show_tree=False, highlight=()):
    code, out = run(*cmd) if cmd else (None, "")
    res = {"title": title, "why": why, "code": code, "out": out, "checks": [],
           "cmd": ("python3 " + " ".join('"%s"' % c if " " in c else c for c in cmd)) if cmd else ""}
    for label, fn in checks:
        try:
            ok = bool(fn(code, out))
        except Exception as e:                                  # noqa: BLE001
            ok, label = False, label + " (error: %s)" % e
        res["checks"].append([label, ok])
    if show_tree:
        res["tree"] = [[t, any(h in rel for h in highlight)] for t, rel in tree(DATA)]
    steps.append(res)
    return code, out


def w(rel, text):
    p = os.path.join(DATA, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(text)


def ledger():
    try:
        return json.load(open(os.path.join(DATA, ".resu", "documents.json"), encoding="utf-8"))
    except (IOError, ValueError):
        return {}


def store_key(path):
    m = re.search(r'const STORE = "([^"]*)"', open(path, encoding="utf-8").read())
    return m.group(1) if m else None


SCORE = """---
depth: essentials
counts:
  asks_total: 3
  must: 3
  you_have: %d
  a_reader_would_find: %d
  unscored: 0
---

| Ask | Necessity | State | Evidence | Note |
|---|---|---|---|---|
%s
"""

shutil.rmtree(SCR, ignore_errors=True)
w("2 My record/facts.md", "# Facts\n\n```\nid: fact-roster\ntext: Rostered 35 casual staff in Deputy\n```\n")
w("answers.md", "---\ndepth: essentials\n---\n# Answers\n")
shutil.copy(os.path.join(REPO, "docs", "review", "sample-cv.md"), os.path.join(DATA, "sample.md"))
os.makedirs(os.path.join(DATA, "1 About me"), exist_ok=True)
shutil.move(os.path.join(DATA, "sample.md"), os.path.join(DATA, "1 About me", "Alex Morgan CV.md"))
CV = os.path.join(DATA, "1 About me", "Alex Morgan CV.md")

run("scripts/jobs.py", "new", "--role", "Operations Coordinator", "--employer", "Northside Community Care",
    "--closes", "2026-10-03")
run("scripts/jobs.py", "new", "--role", "Venue Manager", "--employer", "Riverbend Events", "--closes", "2026-09-30")
A, B = "northside-community-care-operations-coordinator-2026-09", "riverbend-events-venue-manager-2026-09"
w("3 Jobs/%s/scorecard.md" % A, SCORE % (3, 2, "\n".join([
    "| Rostering a casual workforce | must | page | Built and maintained weekly rosters for 35 casual staff | |",
    "| Supplier and contract management | must | page | Managed relationships with 14 suppliers | |",
    "| Experience in community services | must | missing | | Nothing on the record yet |"])))
w("3 Jobs/%s/scorecard.md" % B, SCORE % (3, 3, "\n".join([
    "| Running a function venue | must | page | Coordinated day-to-day operations for a 400-guest function venue | |",
    "| Budget tracking and reporting | must | page | Tracked event budgets against actual spend | |",
    "| Leading a casual team | must | buried | Built and maintained weekly rosters for 35 casual staff | Say lead |"])))

step("1. Two jobs for one fake person",
     "Alex Morgan (the fictional CV in docs/review) is applying to two employers. Each job has its own folder "
     "and scorecard. The CV and facts are shared.",
     ["scripts/jobs.py", "list"],
     checks=[("both jobs listed", lambda c, o: A in o and B in o)])

step("2. Build the studio for the Northside job",
     "Only --job is passed. Role and employer are read from the job's record.",
     ["scripts/build_studio.py", "--cv", CV, "--job", "northside",
      "--scorecard", os.path.join(DATA, "3 Jobs", A, "scorecard.md")],
     checks=[("exit code 0", lambda c, o: c == 0),
             ("written into the job's own documents folder",
              lambda c, o: "Northside Community Care - Operations Coordinator/Operations Coordinator - Northside Community Care - Studio.html" in o),
             ("asks loaded from this job's scorecard", lambda c, o: "asks   : 3" in o),
             ("store key is the same rule as before, role and employer",
              lambda c, o: "cvwb:operations-coordinator-northside-community-care" in o)])

step("3. Build the studio for the Riverbend job",
     "", ["scripts/build_studio.py", "--cv", CV, "--job", "riverbend",
          "--scorecard", os.path.join(DATA, "3 Jobs", B, "scorecard.md")],
     checks=[("exit code 0", lambda c, o: c == 0),
             ("written into Riverbend's folder", lambda c, o: "Riverbend Events - Venue Manager/" in o),
             ("its own browser store", lambda c, o: "cvwb:venue-manager-riverbend-events" in o)])

SA = os.path.join(DOCS, "Northside Community Care - Operations Coordinator",
                  "Operations Coordinator - Northside Community Care - Studio.html")
SB = os.path.join(DOCS, "Riverbend Events - Venue Manager", "Venue Manager - Riverbend Events - Studio.html")

step("4. The old way still works, and keeps the same browser store",
     "Built with --role and --employer and no --job, as every existing command in SKILL.md does today. "
     "It goes to the top of the documents folder, and its store key matches the job build, so marks a person "
     "already made are still there.",
     ["scripts/build_studio.py", "--cv", CV, "--role", "Operations Coordinator",
      "--employer", "Northside Community Care", "--out", os.path.join(SCR, "old-way-studio.html")],
     checks=[("exit code 0", lambda c, o: c == 0),
             ("same store key as the job build",
              lambda c, o: store_key(os.path.join(SCR, "old-way-studio.html")) == store_key(SA)
              == "cvwb:operations-coordinator-northside-community-care")])

browser = os.environ.get("CV_BROWSER") or next(iter(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome")), "")
if browser:
    ENV["CV_BROWSER"] = browser
step("5. Print the Northside CV to PDF",
     "render_cv.py with --job. The PDF lands beside that job's studio.",
     ["scripts/render_cv.py", CV, "--job", "northside", "--pdf"],
     checks=[("exit code 0", lambda c, o: c == 0),
             ("a CV PDF is in Northside's folder", lambda c, o: glob.glob(os.path.join(
                 DOCS, "Northside Community Care - Operations Coordinator", "*Northside Community Care*CV.pdf"))),
             ("no PDF landed in Riverbend's folder", lambda c, o: not glob.glob(os.path.join(
                 DOCS, "Riverbend Events - Venue Manager", "*.pdf")))])

step("6. Where everything landed",
     "Each job's documents are in their own folder. Green rows are the two jobs.",
     show_tree=True, highlight=("Northside", "Riverbend", "northside", "riverbend"),
     checks=[("every studio and PDF record says which job it is for", lambda c, o: all(
         r.get("job") in (A, B) for k, r in ledger().items() if "Northside" in k or "Riverbend" in k)),
             ("the old-way studio has no job", lambda c, o: any(
                 not r.get("job") for k, r in ledger().items() if "old-way" in k))])

step("7. The documents list shows the job beside each application", "",
     ["scripts/documents.py"],
     checks=[("Northside job named", lambda c, o: "[job %s]" % A in o),
             ("Riverbend job named", lambda c, o: "[job %s]" % B in o)])

step("8. check.py on one job finds the shared facts ledger",
     "The job folder has no facts.md of its own, which is normal now. check.py reads the person's one.",
     ["scripts/check.py", "--job", "riverbend"],
     checks=[("reads facts.md from the person's folder", lambda c, o: "facts from ~/.resu-studio/2 My record/facts.md" in o),
             ("counts the fact", lambda c, o: "facts: 1" in o),
             ("does not say Phase 2 has not run for facts", lambda c, o: "No facts.md" not in o)])

step("9. check.py on the person's folder points at --job", "",
     ["scripts/check.py"],
     checks=[("hints to run check.py --job", lambda c, o: "check.py --job <id>" in o)])

step("10. A job that does not exist is refused, with the real names",
     "", ["scripts/build_studio.py", "--cv", CV, "--job", "acme"],
     checks=[("exit code 3", lambda c, o: c == 3), ("lists the jobs", lambda c, o: A in o and B in o)])

json.dump({"steps": steps, "studios": [SA, SB]},
          open(os.path.join(SCR, "results.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
total = sum(len(s["checks"]) for s in steps)
passed = sum(ok for s in steps for _, ok in s["checks"])
print("%d of %d checks passed" % (passed, total))
for s in steps:
    for label, ok in s["checks"]:
        if not ok:
            print("FAIL", s["title"], "|", label, "\n", s["out"][-800:])
sys.exit(0 if passed == total else 1)
