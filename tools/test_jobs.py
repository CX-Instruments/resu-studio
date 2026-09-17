"""Test run for scripts/jobs.py (steps 1 and 2 of docs/multi-job-plan.md).

Runs the real commands against a fake person's folder in a temp directory and checks
the results. Writes step2-results.json beside the temp folder for screenshots.

    python3 tools/test_jobs.py          prints "N of N checks passed", exit 1 on any fail
"""
import hashlib, json, os, shutil, subprocess, sys, tempfile, time

SKILL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "skills", "resu-studio")
SCR = os.path.join(tempfile.gettempdir(), "resu-test-jobs")
os.makedirs(SCR, exist_ok=True)
DATA = os.path.join(SCR, "fake-home", ".resu-studio")
ENV = dict(os.environ, CLAUDE_PLUGIN_DATA=DATA)
steps = []


def run(*args):
    p = subprocess.run([sys.executable] + list(args), cwd=SKILL, env=ENV,
                       capture_output=True, text=True)
    out = (p.stdout + p.stderr).replace(DATA, "~/.resu-studio")
    return p.returncode, out.rstrip()


def tree(root=DATA):
    lines = []
    def walk(d, pre):
        names = sorted(os.listdir(d), key=lambda n: (not os.path.isdir(os.path.join(d, n)), n.lower()))
        for i, n in enumerate(names):
            last = i == len(names) - 1
            full = os.path.join(d, n)
            lines.append((pre + ("└── " if last else "├── ") + n + ("/" if os.path.isdir(full) else ""),
                          os.path.relpath(full, root)))
            if os.path.isdir(full):
                walk(full, pre + ("    " if last else "│   "))
    walk(root, "")
    return lines


def hashes(root=DATA):
    out = {}
    for d, _, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            out[os.path.relpath(p, root)] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def step(title, why, cmd=None, checks=None, show_tree=False, highlight=(), extra=None):
    code, out = run(*cmd) if cmd else (None, "")
    res = {"title": title, "why": why,
           "cmd": ("python3 " + " ".join(('"%s"' % c if " " in c else c) for c in cmd)) if cmd else "",
           "code": code, "out": out, "checks": [], "extra": extra}
    for label, fn in (checks or []):
        try:
            ok = bool(fn(code, out))
        except Exception as e:
            ok = False
            label += " (error: %s)" % e
        res["checks"].append([label, ok])
    if show_tree:
        res["tree"] = [[t, any(rel.startswith(h) for h in highlight)] for t, rel in tree()]
    steps.append(res)
    return code, out


def w(rel, text):
    p = os.path.join(DATA, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(text)


# ---------------------------------------------------------------- a fake person, old layout
shutil.rmtree(os.path.join(SCR, "fake-home"), ignore_errors=True)
w("facts.md", "# Facts\n\nfact-1: Built monthly reporting pack for 40 clinics.\n")
w("answers.md", "---\ndepth: essentials\n---\n# Answers\n")
w("cv-source/Sam Rivera CV.md", "# Sam Rivera\n\nsam.rivera@example.com\n")
w("cv-source/Harbourview advert.txt", "Senior Data Analyst, Harbourview Health\n")
w("asks.md", "# Asks\n\nask-1: SQL\nask-2: Power BI\n")
w("scorecard-before.md", "---\njob: harbourview-health-senior-data-analyst\ndepth: essentials\ncounts:\n  asks_total: 14\n  must: 9\n  you_have: 11\n  a_reader_would_find: 6\n  unscored: 5\n---\n")
w("scorecard.md", "---\njob: harbourview-health-senior-data-analyst\ndepth: essentials\ncounts:\n  asks_total: 14\n  must: 9\n  you_have: 11\n  a_reader_would_find: 10\n  unscored: 5\n---\n")
w("proposals.md", "# Proposals\n\nP1 ...\n")
w("cv-decisions.json", '{"marks": {}}\n')
w("cv-tailored.md", "# Sam Rivera\n\nTailored.\n")
w("cv-tailored-archive.md", "# Archive\n")
w("cover-letter-tailored.md", "Dear Hiring Manager,\n")
w("my own notes.md", "Personal notes the person put here themselves.\n")
w("_Your Documents Are Here/Senior Data Analyst - Harbourview Health - Studio.html", "<html></html>")
w("_Your Documents Are Here/Sam Rivera - Senior Data Analyst - Harbourview Health - 20260910 - CV.pdf", "%PDF")
w("_Your Documents Are Here/Sam Rivera - Reporting Lead - Old Mill Foods - 20260801 - CV.pdf", "%PDF")
docs = os.path.join(DATA, "_Your Documents Are Here")
w("documents.json", json.dumps({
    "_Your Documents Are Here/Sam Rivera - Reporting Lead - Old Mill Foods - 20260801 - CV.pdf":
        {"role": "Reporting Lead", "employer": "Old Mill Foods", "kind": "cv", "source": "cv-old.md",
         "name": "Sam Rivera - Reporting Lead - Old Mill Foods - 20260801 - CV.pdf",
         "path": os.path.join(docs, "Sam Rivera - Reporting Lead - Old Mill Foods - 20260801 - CV.pdf"),
         "written": "2026-08-01 10:00"},
    "_Your Documents Are Here/Senior Data Analyst - Harbourview Health - Studio.html":
        {"role": "Senior Data Analyst", "employer": "Harbourview Health", "kind": "studio",
         "source": "cv-tailored.md", "name": "Senior Data Analyst - Harbourview Health - Studio.html",
         "path": os.path.join(docs, "Senior Data Analyst - Harbourview Health - Studio.html"),
         "written": "2026-09-10 14:02"},
    "_Your Documents Are Here/Sam Rivera - Senior Data Analyst - Harbourview Health - 20260910 - CV.pdf":
        {"role": "Senior Data Analyst", "employer": "Harbourview Health", "kind": "cv",
         "source": "cv-tailored.md", "name": "Sam Rivera - Senior Data Analyst - Harbourview Health - 20260910 - CV.pdf",
         "path": os.path.join(docs, "Sam Rivera - Senior Data Analyst - Harbourview Health - 20260910 - CV.pdf"),
         "written": "2026-09-10 14:05"},
}, indent=2))
original = hashes()

LOOSE = ("asks.md", "scorecard", "proposals.md", "cv-decisions.json", "cv-tailored", "cover-letter")
step("1. Before: a folder from the old single-job layout",
     "A fake person, Sam Rivera, who used the plugin before jobs had folders. The highlighted files belong to one "
     "application and sit loose next to the files that belong to Sam. \"my own notes.md\" is a file Sam put there.",
     show_tree=True, highlight=LOOSE)

step("2. Listing jobs notices the loose files",
     "No jobs exist yet, and the loose files are named so the assistant knows to offer bringing them in.",
     ["scripts/jobs.py", "list"],
     checks=[("exit code 0", lambda c, o: c == 0),
             ("names the 8 loose working files", lambda c, o: "8 working files" in o),
             ("does not name facts.md, answers.md or my own notes.md",
              lambda c, o: all(x not in o for x in ("facts.md", "answers.md", "my own notes")))])

before_dry = hashes()
step("3. Dry run: says what would happen, changes nothing",
     "The job is guessed from the newest document on record (Harbourview Health, 10 Sept), "
     "not the older Old Mill Foods one.",
     ["scripts/jobs.py", "adopt", "--dry-run"],
     checks=[("exit code 0", lambda c, o: c == 0),
             ("guesses Senior Data Analyst at Harbourview Health",
              lambda c, o: "Senior Data Analyst" in o and "Harbourview Health" in o),
             ("says the guess must be checked with the person", lambda c, o: "check with the person" in o),
             ("stage read as Ready, because a cover letter exists", lambda c, o: "stage    : Ready" in o),
             ("not one file in the folder changed", lambda c, o: hashes() == before_dry)])

step("4. Adopt: copy the files into a new job",
     "The real run.",
     ["scripts/jobs.py", "adopt"],
     checks=[("exit code 0", lambda c, o: c == 0),
             ("all 8 working files copied", lambda c, o: "brought 8 files" in o and o.count(".md")+o.count(".json") >= 8),
             ("2 earlier Harbourview documents tagged with the job", lambda c, o: "2 earlier documents" in o)])

JOB = "harbourview-health-senior-data-analyst-2026-09"
after = hashes()
step("5. After: the job folder, and the originals still in place",
     "Green rows are new. Every file that was there before is still there, byte for byte.",
     show_tree=True, highlight=("jobs", ".adopted-into-jobs.json"),
     checks=[("every original file is unchanged",
              lambda c, o: all(after.get(k) == v for k, v in original.items() if k != "documents.json")),
             ("the job copies are identical to the originals",
              lambda c, o: all(after["jobs/%s/%s" % (JOB, n)] == original[n] for n in
                               ("asks.md", "scorecard.md", "scorecard-before.md", "proposals.md",
                                "cv-decisions.json", "cv-tailored.md", "cv-tailored-archive.md",
                                "cover-letter-tailored.md"))),
             ("facts.md, answers.md, cv-source and my own notes.md were not copied into the job",
              lambda c, o: not any(k.startswith("jobs/") and os.path.basename(k) in
                                   ("facts.md", "answers.md", "my own notes.md", "Sam Rivera CV.md")
                                   for k in after))])

rec = json.load(open(os.path.join(DATA, "jobs", JOB, "job.json")))
ledger = json.load(open(os.path.join(DATA, "documents.json")))
step("6. The job's record, job.json",
     "Stage, depth and both scores were read from the old files. The Old Mill Foods document was left alone.",
     extra={"json": rec, "ledger": {k.split("/")[-1]: v.get("job", "(no job)") for k, v in ledger.items()}},
     checks=[("stage is Ready", lambda c, o: rec["stage"] == "Ready"),
             ("depth is essentials", lambda c, o: rec["depth"] == "essentials"),
             ("before score 6 of 14 found, after 10 of 14",
              lambda c, o: rec["scores"]["before"]["a_reader_would_find"] == 6
              and rec["scores"]["after"]["a_reader_would_find"] == 10),
             ("Old Mill Foods document has no job", lambda c, o: not any(
                 v.get("job") for v in ledger.values() if v["employer"] == "Old Mill Foods")),
             ("both Harbourview documents point at the job", lambda c, o: sum(
                 1 for v in ledger.values() if v.get("job") == JOB) == 2)])

step("7. Running adopt again does nothing",
     "It remembers what it already brought in, so it never offers the same files twice.",
     ["scripts/jobs.py", "adopt"],
     checks=[("refused with exit code 4", lambda c, o: c == 4),
             ("says there is nothing to bring in", lambda c, o: "no loose working files" in o)])

time.sleep(1.1)
with open(os.path.join(DATA, "cv-tailored.md"), "a", encoding="utf-8") as fh:
    fh.write("\nA line added later, the old way.\n")
step("8. Somebody keeps working in the old place",
     "cv-tailored.md at the top level was edited after the job was made. Listing jobs notices just that one file.",
     ["scripts/jobs.py", "list"],
     checks=[("notices exactly 1 file", lambda c, o: "1 working file" in o and "(cv-tailored.md)" in o)])

job_cv_before = hashes()["jobs/%s/cv-tailored.md" % JOB]
step("9. Adopting the changed file keeps both versions",
     "The job already has a cv-tailored.md with different wording, so neither is written over.",
     ["scripts/jobs.py", "adopt"],
     checks=[("exit code 0", lambda c, o: c == 0),
             ("the job's own cv-tailored.md is unchanged",
              lambda c, o: hashes()["jobs/%s/cv-tailored.md" % JOB] == job_cv_before),
             ("the newer one sits beside it with a dated name",
              lambda c, o: os.path.isfile(os.path.join(DATA, "jobs", JOB,
                                                       "cv-tailored (brought in %s).md" % time.strftime("%Y-%m-%d"))))])

# ---------------------------------------------------------------- nothing on record
os.remove(os.path.join(DATA, "documents.json"))
w("asks.md", "# Asks for something else\n")
step("10. No documents on record: it asks instead of guessing",
     "documents.json removed, and asks.md changed. With nothing saying which job it was for, adopt refuses.",
     ["scripts/jobs.py", "adopt"],
     checks=[("refused with exit code 4", lambda c, o: c == 4),
             ("tells the assistant to ask the person", lambda c, o: "Ask the person" in o)])

step("11. Given a role and employer, it goes into a new job",
     "",
     ["scripts/jobs.py", "adopt", "--role", "BI Developer", "--employer", "Bluegum Energy"],
     checks=[("exit code 0", lambda c, o: c == 0),
             ("new job made for Bluegum Energy", lambda c, o: "bluegum-energy-bi-developer-2026-09" in o)])

step("12. Both jobs, side by side",
     "Step 1 commands still work alongside the new ones.",
     ["scripts/jobs.py", "list"],
     checks=[("both jobs listed", lambda c, o: "harbourview" in o and "bluegum" in o),
             ("no loose-files notice left", lambda c, o: "working file" not in o)])


run("scripts/jobs.py", "stage", "bluegum", "Rejected")
step("13. A closed job does not block applying again, and documents stay apart",
     "Bluegum Energy was set to Rejected. A new job for the same role gets its own documents folder with (2) on the end.",
     ["scripts/jobs.py", "new", "--role", "BI Developer", "--employer", "Bluegum Energy", "--closes", "2026-10-15"],
     checks=[("exit code 0", lambda c, o: c == 0),
             ("new id ends -2", lambda c, o: "bluegum-energy-bi-developer-2026-09-2" in o),
             ("documents folder is Bluegum Energy - BI Developer (2)", lambda c, o: "Bluegum Energy - BI Developer (2)" in o)])

json.dump(steps, open(os.path.join(SCR, "step2-results.json"), "w"), indent=1, ensure_ascii=False)
total = sum(len(s["checks"]) for s in steps)
passed = sum(ok for s in steps for _, ok in s["checks"])
print("%d of %d checks passed" % (passed, total))
for s in steps:
    for label, ok in s["checks"]:
        if not ok:
            print("FAIL", s["title"], label)
sys.exit(0 if passed == total else 1)
