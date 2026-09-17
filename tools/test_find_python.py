"""Tests for scripts/find_python.sh and scripts/find_python.ps1: finding Python where it hides.

Builds fake installs in a temp folder: a Miniconda Python in a home folder that is not on
the PATH, an "old" Python that reports version 3.6, and a broken one. Runs the finder the
way an assistant would and checks it picks the right one, remembers it, and honours
RESU_PYTHON.

    python3 tools/test_find_python.py     prints "N of N checks passed", exit 1 on any fail

The PowerShell finder is run too when PowerShell is on this machine (it always is on
Windows). Where it is not, its checks are reported as skipped, by name.
"""
import os, shutil, subprocess, sys, tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(REPO, "skills", "resu-studio", "scripts")
SCR = os.path.join(tempfile.gettempdir(), "resu-test-find-python")
WIN = os.name == "nt"
steps = []


def check(title, ok, detail=""):
    steps.append((title, bool(ok), detail))


def fake_python(path, version="3.11", works=True):
    """A stand-in python that answers the finder's question like a real one of that version."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if WIN:
        # A copied python.exe needs its DLLs, so a venv's launcher is used instead: it runs
        # the real Python and reports its own path as sys.executable. A venv cannot pretend
        # to be an older version, so that one check is skipped on Windows.
        if works:
            v = path + ".venv"
            subprocess.run([sys.executable, "-m", "venv", "--without-pip", v], check=True)
            shutil.copy(os.path.join(v, "Scripts", "python.exe"), path)
            shutil.copy(os.path.join(v, "pyvenv.cfg"), os.path.join(os.path.dirname(path), "pyvenv.cfg"))
        else:
            open(path, "w").write("not a program")
        return
    major, minor = version.split(".")
    body = ('#!/bin/sh\nexec "%s" -c "import sys; sys.version_info=(%s,%s); '
            'sys.executable=\'%s\'; exec(sys.argv[1])" "$2"\n' % (sys.executable, major, minor, path)
            if works else "#!/bin/sh\nexit 9009\n")
    with open(path, "w") as fh:
        fh.write(body)
    os.chmod(path, 0o755)


def run_sh(env):
    p = subprocess.run(["sh", os.path.join(SCRIPTS, "find_python.sh")], env=env,
                       capture_output=True, text=True)
    return p.returncode, p.stdout.strip().splitlines()[-1] if p.stdout.strip() else "", p.stderr


shutil.rmtree(SCR, ignore_errors=True)
HOME = os.path.join(SCR, "home")
CONFIG = os.path.join(SCR, "config")
conda = os.path.join(HOME, "miniconda3", "python.exe" if WIN else "bin/python")
fake_python(conda, "3.11")
old = os.path.join(SCR, "old", "python")
if not WIN:
    fake_python(old, "3.6")
broken = os.path.join(SCR, "broken", "python")
fake_python(broken, works=False)

base = {k: v for k, v in os.environ.items() if not k.startswith(("CONDA", "RESU_"))}
base.update(HOME=HOME, USERPROFILE=HOME, RESU_STUDIO_CONFIG=CONFIG)

if shutil.which("sh"):
    code, found, err = run_sh(dict(base))
    check("sh: finds Miniconda in the home folder, not on the PATH", code == 0 and found == conda, found or err)
    check("sh: remembers it in python.txt", open(os.path.join(CONFIG, "python.txt")).read().strip() == conda)

    if not WIN:
        code, found, err = run_sh(dict(base, RESU_PYTHON=old))
        check("sh: skips a Python older than 3.8 even when named in RESU_PYTHON", code == 0 and found == conda, found)

    code, found, err = run_sh(dict(base, RESU_PYTHON=broken))
    check("sh: skips a python that does not run (like the Store placeholder)", code == 0 and found == conda, found)

    other = os.path.join(SCR, "chosen", "python.exe" if WIN else "python")
    fake_python(other, "3.12")
    code, found, err = run_sh(dict(base, RESU_PYTHON=other))
    check("sh: RESU_PYTHON wins when it works", code == 0 and found == other, found)

    os.remove(other)
    code, found, err = run_sh(dict(base))
    check("sh: a remembered path that is gone is not trusted", code == 0 and found == conda, found)

    env = dict(base, CONDA_PREFIX=os.path.join(SCR, "env-active"))
    active = os.path.join(SCR, "env-active", "python.exe" if WIN else "bin/python")
    fake_python(active, "3.10")
    open(os.path.join(CONFIG, "python.txt"), "w").write("")
    code, found, err = run_sh(env)
    check("sh: an active conda environment comes before the base install", code == 0 and found == active, found)
else:
    check("sh: not available on this machine, sh checks skipped", True)

ps = shutil.which("pwsh") or shutil.which("powershell")
if ps and WIN:
    open(os.path.join(CONFIG, "python.txt"), "w").write("")
    p = subprocess.run([ps, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                        os.path.join(SCRIPTS, "find_python.ps1")], env=dict(base),
                       capture_output=True, text=True)
    found = p.stdout.strip().splitlines()[-1] if p.stdout.strip() else ""
    check("PowerShell: finds Miniconda in the home folder", p.returncode == 0 and os.path.normcase(found) == os.path.normcase(conda),
          found or p.stderr)
    p = subprocess.run([ps, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                        os.path.join(SCRIPTS, "find_python.ps1")], env=dict(base, RESU_PYTHON=broken),
                       capture_output=True, text=True)
    found = p.stdout.strip().splitlines()[-1] if p.stdout.strip() else ""
    check("PowerShell: skips a python.exe that does not run", p.returncode == 0 and os.path.normcase(found) == os.path.normcase(conda), found)
else:
    check("PowerShell: skipped, it only runs on Windows", True)

total, passed = len(steps), sum(ok for _, ok, _ in steps)
print("%d of %d checks passed" % (passed, total))
for title, ok, detail in steps:
    print("  %s %s%s" % ("ok  " if ok else "FAIL", title, "" if ok else "  -> " + str(detail)))
sys.exit(0 if passed == total else 1)
