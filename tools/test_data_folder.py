"""Test run for step 4b of docs/multi-job-plan.md: where a person's private files live.

Builds a fake computer in a temp folder: a home folder holding work from an older
version, a project with the skill installed into `.agents/skills/resu-studio` the way
`npx skills add` does, and a second install for the whole computer. Every script runs
as it would from those installs, with HOME pointed at the fake home.

    python3 tools/test_data_folder.py     prints "N of N checks passed", exit 1 on any fail

Needs git on the PATH for the checks that prove nothing private can be committed.
"""
import hashlib, json, os, re, shutil, subprocess, sys, tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_SRC = os.path.join(REPO, "skills", "resu-studio")
SCR = os.path.join(tempfile.gettempdir(), "resu-test-data-folder")
HOME = os.path.join(SCR, "home")
PROJECT = os.path.join(SCR, "Career")
P_SKILL = os.path.join(PROJECT, ".agents", "skills", "resu-studio")
G_SKILL = os.path.join(HOME, ".claude", "skills", "resu-studio")
OLD = os.path.join(HOME, ".resu-studio")
CHOSEN = os.path.join(PROJECT, "Resu - CV Builder")
steps = []

ENV = {k: v for k, v in os.environ.items()
       if k not in ("CLAUDE_PLUGIN_DATA", "PLUGIN_DATA", "RESU_STUDIO_CONFIG")}
ENV.update(HOME=HOME, USERPROFILE=HOME)


def short(text):
    return text.replace(PROJECT, "D:/Career").replace(HOME, "~")


def run(skill, *args, cwd=None):
    p = subprocess.run([sys.executable] + list(args), cwd=cwd or skill, env=ENV,
                       capture_output=True, text=True, encoding="utf-8")
    return p.returncode, short((p.stdout + p.stderr).rstrip())


def git(*args):
    p = subprocess.run(["git"] + list(args), cwd=PROJECT, env=ENV, capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).rstrip()


def tree(root, skip=(".git", ".agents")):
    lines = []
    def walk(d, pre):
        names = sorted((n for n in os.listdir(d) if n not in skip),
                       key=lambda n: (not os.path.isdir(os.path.join(d, n)), n.lower()))
        for i, n in enumerate(names):
            last, full = i == len(names) - 1, os.path.join(d, n)
            lines.append([pre + ("└── " if last else "├── ") + n + ("/" if os.path.isdir(full) else ""),
                          os.path.relpath(full, root)])
            if os.path.isdir(full):
                walk(full, pre + ("    " if last else "│   "))
    walk(root, "")
    return lines


def hashes(root):
    out = {}
    for d, _, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            if os.path.relpath(p, root) == "locations.json":
                continue
            out[os.path.relpath(p, root)] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def step(title, why, skill=None, cmd=None, checks=(), trees=(), cwd=None, out=None):
    code, text = run(skill, *cmd, cwd=cwd) if cmd else (None, out or "")
    res = {"title": title, "why": why, "code": code, "out": text, "checks": [], "trees": [],
           "cmd": ("python3 " + " ".join('"%s"' % c if " " in c else c for c in cmd)) if cmd else ""}
    res["cmd"] = short(res["cmd"])
    for label, fn in checks:
        try:
            ok = bool(fn(code, text))
        except Exception as e:                                  # noqa: BLE001
            ok, label = False, label + " (error: %s)" % e
        res["checks"].append([label, ok])
    for label, root, highlight in trees:
        res["trees"].append([label, [[t, any(h in rel for h in highlight)] for t, rel in tree(root)]])
    steps.append(res)
    return code, text


def w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def copy_skill(dest):
    shutil.copytree(SKILL_SRC, dest, ignore=shutil.ignore_patterns("__pycache__", "data", "data-location.txt"))


# ---------------------------------------------------------------- a fake computer
shutil.rmtree(SCR, ignore_errors=True)
copy_skill(P_SKILL)
copy_skill(G_SKILL)
w(os.path.join(PROJECT, "notes.md"), "The person's own project notes.\n")

# Work left by an older version, in the old shared folder, old layout.
w(os.path.join(OLD, "facts.md"), "# Facts\n")
w(os.path.join(OLD, "answers.md"), "# Answers\n")
w(os.path.join(OLD, "cv-source", "Sam Rivera CV.md"), "# Sam Rivera\n")
w(os.path.join(OLD, "cv-source", "Harbourview advert.txt"), "Senior Data Analyst\n")
w(os.path.join(OLD, "scorecard.md"), "---\ndepth: essentials\ncounts:\n  asks_total: 10\n  must: 6\n  you_have: 8\n  a_reader_would_find: 5\n  unscored: 4\n---\n")
w(os.path.join(OLD, "cv-tailored.md"), "# Sam Rivera\n")
w(os.path.join(OLD, "location.bak"), "not ours\n")
studio_old = os.path.join(OLD, "_Your Documents Are Here", "Senior Data Analyst - Harbourview Health - Studio.html")
w(studio_old, "<html></html>")
w(os.path.join(OLD, "documents.json"), json.dumps({
    "_Your Documents Are Here/Senior Data Analyst - Harbourview Health - Studio.html": {
        "role": "Senior Data Analyst", "employer": "Harbourview Health", "kind": "studio",
        "source": "cv-tailored.md", "name": os.path.basename(studio_old), "path": studio_old,
        "written": "2026-09-07 10:00"}}, indent=2))
old_hashes = hashes(OLD)
subprocess.run(["git", "init", "-q"], cwd=PROJECT, env=ENV)

# ---------------------------------------------------------------- nothing chosen
step("1. A fresh install inside a project: nothing is chosen, so nothing happens",
     "The skill was installed into D:/Career/.agents/skills the way npx does. Asked for the facts ledger, it "
     "stops instead of using the older work it could find in the home folder.",
     P_SKILL, ["scripts/paths.py", "--facts"],
     checks=[("exit code 6", lambda c, o: c == 6),
             ("tells the assistant to ask the person", lambda c, o: "ask where their files should live" in o),
             ("no folder was made in the project", lambda c, o: not os.path.exists(CHOSEN)),
             ("no folder was made in the home folder", lambda c, o: not os.path.exists(os.path.join(HOME, "Resu - CV Builder"))),
             ("the older work was not touched", lambda c, o: hashes(OLD) == old_hashes)])

step("2. Other scripts stop the same way, with no crash", "",
     P_SKILL, ["scripts/jobs.py", "list"],
     checks=[("exit code 6", lambda c, o: c == 6), ("no Python traceback", lambda c, o: "Traceback" not in o)])

step("3. --status says what to offer, and what already exists",
     "This is what the assistant reads before asking the person where their files should live.",
     P_SKILL, ["scripts/paths.py", "--status"],
     checks=[("says NOT CHOSEN", lambda c, o: "NOT CHOSEN YET" in o),
             ("knows it is inside the project", lambda c, o: "inside the project D:/Career" in o),
             ("offers D:/Career/Resu - CV Builder", lambda c, o: "project : D:/Career/Resu - CV Builder" in o),
             ("offers the home folder too", lambda c, o: "home    : ~/Resu - CV Builder" in o),
             ("lists the older work in ~/.resu-studio, counts only",
              lambda c, o: "~/.resu-studio" in o and "a facts ledger" in o and "working files for one earlier application" in o),
             ("does not print anybody's CV", lambda c, o: "Sam Rivera" not in o)])

# ---------------------------------------------------------------- choosing, bringing the old work in
step("4. The person chose the project folder and to bring their earlier work in", "",
     P_SKILL, ["scripts/paths.py", "--choose", "project", "--bring", OLD],
     checks=[("exit code 0", lambda c, o: c == 0),
             ("its own settings file is not reported as left behind", lambda c, o: "locations.json" not in o),
             ("made the four folders", lambda c, o: all(os.path.isdir(os.path.join(CHOSEN, n)) for n in
                                                      ("1 About me", "2 My record", "3 Jobs", "4 Finished documents"))),
             ("the .gitignore holds *", lambda c, o: "*" in open(os.path.join(CHOSEN, ".gitignore")).read().split()),
             ("a README says it is private", lambda c, o: "private" in open(os.path.join(CHOSEN, "README.txt")).read()),
             ("the CV went to 1 About me", lambda c, o: os.path.isfile(os.path.join(CHOSEN, "1 About me", "Sam Rivera CV.md"))),
             ("facts.md went to 2 My record", lambda c, o: os.path.isfile(os.path.join(CHOSEN, "2 My record", "facts.md"))),
             ("the earlier application's files wait in .resu/from-before-jobs",
              lambda c, o: sorted(os.listdir(os.path.join(CHOSEN, ".resu", "from-before-jobs"))) == ["cv-tailored.md", "scorecard.md"]),
             ("the documents list points at the copied Studio", lambda c, o: all(
                 os.path.isfile(r["path"]) and r["path"].startswith(CHOSEN)
                 for r in json.load(open(os.path.join(CHOSEN, ".resu", "documents.json"))).values())),
             ("a file that is not Resu Studio's was left behind and named", lambda c, o: "location.bak" in o),
             ("nothing in ~/.resu-studio changed", lambda c, o: hashes(OLD) == old_hashes)],
     trees=[("D:/Career after --choose (the skill and .git hidden)", PROJECT, ("Resu - CV Builder",))])

gs = git("status", "--porcelain", "--untracked-files=all")
git("add", "-A")
ls = git("ls-files")
ci = git("check-ignore", "-v", os.path.join(CHOSEN, "1 About me", "Sam Rivera CV.md"))
step("5. git cannot see any of it",
     "The project is a git repository. git status, git add -A, and git check-ignore on the CV.",
     out="$ git status --porcelain --untracked-files=all\n%s\n\n$ git add -A && git ls-files | grep -v .agents\n%s\n\n$ git check-ignore -v \"Resu - CV Builder/1 About me/Sam Rivera CV.md\"\n%s"
         % ("\n".join(l for l in gs[1].splitlines() if ".agents/" not in l)
            + "\n(and %d lines for the skill's own files under .agents/)" % sum(1 for l in gs[1].splitlines() if ".agents/" in l),
            "\n".join(l for l in ls[1].splitlines() if not l.startswith(".agents")), short(ci[1])),
     checks=[("git status lists nothing from Resu - CV Builder", lambda c, o: "Resu - CV Builder" not in gs[1]),
             ("git add -A staged nothing from it", lambda c, o: "Resu - CV Builder" not in ls[1]),
             ("the person's own notes.md is still tracked normally", lambda c, o: "notes.md" in ls[1]),
             ("check-ignore names the folder's own .gitignore", lambda c, o: ci[0] == 0 and "Resu - CV Builder/.gitignore" in ci[1])])

step("6. The choice is remembered", "A new process, no flags: the project folder, decided by this install's choice.",
     P_SKILL, ["scripts/paths.py"],
     checks=[("exit code 0", lambda c, o: c == 0),
             ("uses D:/Career/Resu - CV Builder", lambda c, o: "D:/Career/Resu - CV Builder" in o.splitlines()[1]),
             ("says why", lambda c, o: "chosen for this install" in o)])

step("7. The earlier application becomes a job", "jobs.py adopt finds the files brought in, and guesses the job from the documents list.",
     P_SKILL, ["scripts/jobs.py", "adopt"],
     checks=[("exit code 0", lambda c, o: c == 0),
             ("into a Harbourview Health job", lambda c, o: "harbourview-health-senior-data-analyst" in o),
             ("the job is in 3 Jobs", lambda c, o: any(n.startswith("harbourview") for n in os.listdir(os.path.join(CHOSEN, "3 Jobs")))),
             ("Resu Desk was written to 4 Finished documents", lambda c, o: os.path.isfile(os.path.join(CHOSEN, "4 Finished documents", "Resu Desk.html")))],
     trees=[("Resu - CV Builder after adopt", CHOSEN, ("3 Jobs", "Resu Desk"))])

# ---------------------------------------------------------------- a second install
step("8. An install for the whole computer does not see the project's choice",
     "The same skill, installed in ~/.claude/skills. It is asked separately, and it lists the project's folder as existing work.",
     G_SKILL, ["scripts/paths.py", "--status"],
     checks=[("exit code 0", lambda c, o: c == 0),
             ("NOT CHOSEN for this install", lambda c, o: "NOT CHOSEN YET" in o),
             ("knows it serves the whole computer", lambda c, o: "serves the whole computer" in o),
             ("does not offer a project folder", lambda c, o: "project :" not in o),
             ("lists the project's folder as another install's work", lambda c, o: "D:/Career/Resu - CV Builder" in o and "chosen by another install" in o)])

step("9. It cannot choose a project it is not in", "", G_SKILL, ["scripts/paths.py", "--choose", "project"],
     checks=[("refused, exit 5", lambda c, o: c == 5), ("says why in a sentence", lambda c, o: "not inside a project" in o)])

if os.name != "nt":
    step("10. A Windows path is refused on Linux or a Mac", "", G_SKILL, ["scripts/paths.py", "--choose", "D:\\CVs"],
         checks=[("refused, exit 5", lambda c, o: c == 5), ("says it is a Windows path", lambda c, o: "Windows path" in o)])

w(os.path.join(P_SKILL, "data-location.txt"), os.path.join(SCR, "elsewhere") + "\n")
os.makedirs(os.path.join(SCR, "elsewhere"))
step("11. data-location.txt inside an install still wins", "", P_SKILL, ["scripts/paths.py", "--facts"],
     checks=[("exit code 0", lambda c, o: c == 0),
             ("the pointer's folder is used", lambda c, o: o.endswith("elsewhere/2 My record/facts.md")),
             ("and it is made private too", lambda c, o: os.path.isfile(os.path.join(SCR, "elsewhere", ".gitignore")))])

json.dump({"steps": steps}, open(os.path.join(SCR, "results.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
total = sum(len(s["checks"]) for s in steps)
passed = sum(ok for s in steps for _, ok in s["checks"])
print("%d of %d checks passed" % (passed, total))
for s in steps:
    for label, ok in s["checks"]:
        if not ok:
            print("FAIL", s["title"], "|", label, "\n", s["out"][-900:])
sys.exit(0 if passed == total else 1)
