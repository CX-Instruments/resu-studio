"""Runs the commands SKILL.md documents, as written, in the order an assistant meets them.

Every ```bash block in SKILL.md that calls a script is taken out of the file, its
placeholders filled in for a fictional person and job, and run with bash from a skill
installed inside a project, the way `npx skills add` installs it. A command in the
instructions that no longer matches the scripts fails here, by name, before anybody
follows it.

    python3 tools/test_skill_commands.py     prints "N of N checks passed", exit 1 on any fail

Needs bash (Git Bash on Windows) and a Chromium-family browser for the PDF (CV_BROWSER).
"""
import glob, json, os, re, shutil, subprocess, sys, tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCR = os.path.join(tempfile.gettempdir(), "resu-test-skill-commands")
HOME = os.path.join(SCR, "home")
PROJECT = os.path.join(SCR, "Career")
SKILL = os.path.join(PROJECT, ".agents", "skills", "resu-studio")
DATA = os.path.join(PROJECT, "Resu - CV Builder")
ENV = {k: v for k, v in os.environ.items() if k not in ("CLAUDE_PLUGIN_DATA", "PLUGIN_DATA", "RESU_STUDIO_CONFIG")}
ENV.update(HOME=HOME, USERPROFILE=HOME)
browser = os.environ.get("CV_BROWSER") or next(iter(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome")), "")
if browser:
    ENV["CV_BROWSER"] = browser
steps = []

shutil.rmtree(SCR, ignore_errors=True)
shutil.copytree(os.path.join(REPO, "skills", "resu-studio"), SKILL,
                ignore=shutil.ignore_patterns("__pycache__", "data", "data-location.txt"))
os.makedirs(HOME)

blocks = [b for b in re.findall(r"```bash\n(.*?)```", open(os.path.join(SKILL, "SKILL.md"), encoding="utf-8").read(), re.S)
          if "scripts/" in b]

FILL = {
    "<the job title>": "Operations Coordinator", "<the employer>": "Northside Community Care",
    "<the ad's URL>": "https://example.com/jobs/ops", "YYYY-MM-DD": "2026-10-03",
    "<job id>": "northside", "<their CV>": "Alex Morgan CV", "<variant>": "northside",
}


def fill(block):
    block = re.sub(r"\[(--[^\]]+)\]", r"\1", block)          # optional flags: pass them
    block = re.sub(r"#.*$", "", block, flags=re.M)             # comments
    if "--bring" in block:                                     # nothing older to bring here
        block = "\n".join(l for l in block.splitlines() if "--bring" not in l)
    for k, v in FILL.items():
        block = block.replace(k, v)
    # The Python running this test, quoted, so Windows without a python3 command works too.
    return block.replace("python3 ", '"%s" ' % sys.executable.replace("\\", "/"))


def run_block(n, block, expect=(0,), prepare=None, checks=()):
    if prepare:
        prepare()
    script = fill(block)
    p = subprocess.run(["bash", "-e", "-c", script], cwd=SKILL, env=ENV, capture_output=True, text=True)
    out = (p.stdout + p.stderr).replace(PROJECT, "D:/Career").replace(HOME, "~").rstrip()
    if os.sep == "\\":
        out = out.replace("\\", "/")
    res = {"title": "SKILL.md block %d" % n, "why": "", "cmd": script.strip(), "code": p.returncode,
           "out": out, "checks": [["exit code in %s" % (expect,), p.returncode in expect]]}
    for label, fn in checks:
        try:
            ok = bool(fn(out))
        except Exception as e:                                  # noqa: BLE001
            ok, label = False, label + " (error: %s)" % e
        res["checks"].append([label, ok])
    steps.append(res)


def job_dir():
    return glob.glob(os.path.join(DATA, "3 Jobs", "northside*"))[0]


def w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def phase1_inputs():
    shutil.copy(os.path.join(REPO, "docs", "review", "sample-cv.md"), os.path.join(DATA, "1 About me", "Alex Morgan CV.md"))
    w(os.path.join(DATA, "2 My record", "facts.md"), "# Facts\n\n```\nid: fact-roster\ntext: Built and maintained weekly rosters for 35 casual staff\n```\n")


def phase3_inputs():
    j = job_dir()
    w(os.path.join(j, "asks.md"), "# Asks\n\n```\nid: ask-roster\ntext: Rostering a casual workforce\nnecessity: must\n```\n")
    w(os.path.join(j, "scorecard.md"), "---\ndepth: essentials\ncounts:\n  asks_total: 1\n  must: 1\n  you_have: 1\n  a_reader_would_find: 1\n  unscored: 0\n---\n\n"
      "| Ask | Necessity | State | Evidence | Note |\n|---|---|---|---|---|\n| Rostering a casual workforce | must | page | Built and maintained weekly rosters | |\n")


def phase4_inputs():
    j = job_dir()
    w(os.path.join(j, "proposals.md"), "# Proposals\n\n## P1. Professional experience, first role, first bullet\n\n"
      "**Kind:** wording\n**Line:** professional-experience/0/b0\n"
      "**Currently:** Built and maintained weekly rosters for 35 casual staff in Deputy, cutting last-minute shift gaps from about six a month to one\n"
      "**Suggested:** Rostered a casual workforce of 35 in Deputy, cutting last-minute shift gaps from about six a month to one\n"
      "**Why:** Uses the advertisement's words for the same work.\n**Answers:** ask-roster\n**Draws on:** fact-roster\n"
      "**Costs:** nothing\n**Decision:**\n")
    w(os.path.join(j, "achievements.md"), "# Achievements\n")


def phase6_inputs():
    j = job_dir()
    w(os.path.join(j, "cv-decisions.json"), json.dumps({"cv": "Alex Morgan CV.md", "marks": {}}))


def phase7_inputs():
    j = job_dir()
    w(os.path.join(j, "cover-letter-northside.md"),
      "Alex Morgan\n\n3 October 2026\n\nHiring Manager\nNorthside Community Care\n\nDear Hiring Manager,\n\n"
      "I am applying for the Operations Coordinator role.\n\nKind regards,\nAlex Morgan\n")


plan = {
    -1: dict(checks=[("the finder printed a real python", lambda o: os.path.isfile(o.strip().splitlines()[-1]))]),
    0: dict(checks=[("says NOT CHOSEN", lambda o: "NOT CHOSEN YET" in o)]),
    1: dict(checks=[("made Resu - CV Builder in the project", lambda o: os.path.isdir(os.path.join(DATA, "3 Jobs")))]),
    2: dict(prepare=phase1_inputs, checks=[("started the job", lambda o: "started northside-community-care-operations-coordinator" in o)]),
    3: dict(prepare=phase3_inputs, checks=[("studio in the job's documents folder", lambda o: "4 Finished documents/Northside Community Care - Operations Coordinator/" in o)]),
    4: dict(prepare=phase4_inputs, expect=(0, 1), checks=[("the suggestion reached the studio", lambda o: "1 suggestion loaded" in o)]),
    5: dict(prepare=phase6_inputs, checks=[("assembled into the job's folder", lambda o: os.path.isfile(os.path.join(job_dir(), "cv-northside.md")))]),
    6: dict(expect=(0, 1), checks=[("studio rebuilt from the assembled CV", lambda o: "wrote D:/Career/Resu - CV Builder/4 Finished documents/" in o)]),
    7: dict(prepare=phase7_inputs, checks=[("CV and letter PDFs in the job's documents folder", lambda o: len(glob.glob(os.path.join(
        DATA, "4 Finished documents", "Northside Community Care - Operations Coordinator", "*.pdf"))) == 2)]),
}

steps.append({"title": "Blocks found", "why": "", "cmd": "", "code": None, "out": "%d bash blocks in SKILL.md call a script" % len(blocks),
              "checks": [["SKILL.md has the finder block and the 8 blocks this test knows how to feed",
                          len(blocks) == len(plan)]]})
# The finder block holds a bash line and a PowerShell line. Bash runs the first; the second
# is for Windows and is proven by tools/test_find_python.py there.
finder = [b for b in blocks if "find_python" in b]
blocks = [b for b in blocks if "find_python" not in b]
if finder:
    run_block(0, "\n".join(l for l in finder[0].splitlines() if l.startswith("sh ")), **plan[-1])
for n, block in enumerate(blocks):
    run_block(n + 1, block, **plan.get(n, {}))

json.dump({"steps": steps}, open(os.path.join(SCR, "results.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
total = sum(len(s["checks"]) for s in steps)
passed = sum(ok for s in steps for _, ok in s["checks"])
print("%d of %d checks passed" % (passed, total))
for s in steps:
    for label, ok in s["checks"]:
        if not ok:
            print("FAIL", s["title"], "|", label, "\n$", s["cmd"], "\n", s["out"][-1200:])
sys.exit(0 if passed == total else 1)
