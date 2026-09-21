"""Run every test for the multi-job branch, one after another, and say plainly how it went.

    python tools/run_all_tests.py

Each test builds a fake computer in your temp folder and never touches your real files.
The last line says ALL PASSED, or names each test that did not.
"""
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))

TESTS = [
    ("test_open_studio.py", "single browser launch of the exact generated Studio"),
    ("test_writing.py", "writing modes, approvals, assembly and browser handoff"),
    ("test_pdf_reading_order.py", "default renderer and Studio PDF reading order"),
    ("test_find_python.py", "finding Python, conda installs included"),
    ("test_jobs.py", "jobs, and bringing old work in (steps 1 and 2)"),
    ("test_jobs_build.py", "Studio, PDF and check.py per job (step 3)"),
    ("test_desk.py", "Resu Desk (step 4)"),
    ("test_data_folder.py", "where private files live (step 4b)"),
    ("test_end_to_end.py", "all of it together, from a project install"),
    ("test_skill_commands.py", "every command SKILL.md tells an assistant to run"),
]

NEEDS = []
if shutil.which("git") is None:
    NEEDS.append("git is not installed, so the tests that prove git cannot see private files will fail.")
if shutil.which("bash") is None:
    NEEDS.append("bash is not found. On Windows it comes with Git for Windows as Git Bash; without it "
                 "test_skill_commands.py fails.")
try:
    import playwright  # noqa: F401
except ImportError:
    NEEDS.append("Playwright is not installed, so test_desk.py cannot open the Desk in a browser. "
                 "Install it with: %s -m pip install playwright, then: %s -m playwright install chromium"
                 % (sys.executable, sys.executable))
try:
    import pypdf  # noqa: F401
except ImportError:
    NEEDS.append("pypdf is not installed, so the PDF reading-order suite cannot check extracted text. "
                 "Install it with: %s -m pip install pypdf" % sys.executable)
for n in NEEDS:
    print("note: " + n)
if NEEDS:
    print()

failed = []
for name, what in TESTS:
    start = time.time()
    p = subprocess.run([sys.executable, os.path.join(HERE, name)], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    first = (p.stdout.strip().splitlines() or ["(no output)"])[0]
    ok = p.returncode == 0
    print("%s  %-24s %-48s %s  (%ds)" % ("PASS" if ok else "FAIL", name, what, first, time.time() - start))
    if not ok:
        failed.append(name)
        print("      " + "\n      ".join((p.stdout + p.stderr).strip().splitlines()[-25:]))

print()
print("ALL PASSED" if not failed else "NOT PASSED: " + ", ".join(failed))
sys.exit(0 if not failed else 1)
