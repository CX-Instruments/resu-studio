# Testing Resu Studio on your own computer

Two ways to test, written for Windows and VS Code. Part 1 runs the automatic tests and  
takes about five minutes. Part 2 is trying the plugin for real, the way a person would, with  
a fake CV, and takes longer.

Nothing in either part touches your real CV files. Part 1 works entirely in your temp  
folder. Part 2 uses a new, empty test folder that you can delete afterwards.

---

## Part 1: run the automatic tests

### 1\. Open the repo in VS Code

1.  Open VS Code.
2.  **File > Open Folder**, choose `D:\resu-plugin`.
3.  **Terminal > New Terminal**. A panel opens at the bottom. It is PowerShell.

### 2\. Make sure you are on the branch, with the latest work

Type each line and press Enter:

```
git status --short --branch
git log --oneline -3
```

Check that the current branch and commits are the ones you intend to test. For the
0.7.0 release review, use `review/cv-rewrite-strategy`. After merging, test `main`.
Keep any existing local changes before switching branches.

### 3\. Find your Python

Let the plugin's own finder look for it. This is the same thing an AI assistant runs, so  
it is a test in itself:

```
$PY = powershell -NoProfile -ExecutionPolicy Bypass -File skills\resu-studio\scripts\find_python.ps1
$PY
```

The second line should print the full path to an installed Python 3.8 or newer.
If it prints nothing, or a message saying no Python was found, stop and copy that message  
into the chat: the finder needs fixing before anything else.

From here on, this guide calls that path **PY**. If you open a new terminal later, run the  
first line again.

### 4\. Prepare the browser tests

The Studio and Resu Desk tests open the pages in a real browser using Playwright. It is
only for the test; the plugin itself does not need it.

```
& $PY -m pip install playwright pypdf
& $PY -m playwright install chromium
```

The second line downloads a browser for testing, about 150 MB. You only do this once.
`pypdf` checks the actual PDF's extracted text and reading order. Both packages are
test dependencies; the plugin's runtime scripts still use Python's standard library.

The command tests also need Git Bash. If `Get-Command bash` selects Windows' WSL
launcher, put Git Bash first for this terminal (adjust the install path if needed):

```powershell
$env:PATH = 'C:\Program Files\Git\bin;' + $env:PATH
```

To use an installed Edge for browser and PDF tests instead of a downloaded Chromium:

```powershell
$env:CV_BROWSER = 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
```

### 5\. Run every test

```
& $PY tools\run_all_tests.py
```

You will see one line per test, then a last line.

*   **ALL PASSED** means the automated suites passed. Manual writing-quality and
    release checks still matter; inspect any reported skips before treating browser
    coverage as complete.
*   **NOT PASSED: ...** names the test that failed and shows the end of what it printed. Copy  
    that whole output into the chat and I (or the next assistant) can see what went wrong.

A line starting with `note:` above the results means something is missing: git, Git Bash  
or Playwright. It says what to install.

---

## Part 2: try the plugin for real, with a fake person

This is the real test of what a person experiences. You use an AI tool in VS Code (Claude  
Code, Codex or Copilot), installed into a test folder, with the fake CV that ships in the  
repo.

### 1\. Make an empty test folder with the branch's skill in it

In the same PowerShell terminal (still in `D:\resu-plugin`):

```
New-Item -ItemType Directory "D:\dev resu-studio\.agents\skills" -Force
Copy-Item -Recurse "D:\resu-plugin\skills\resu-studio" "D:\dev resu-studio\.agents\skills\resu-studio"
Copy-Item "D:\resu-plugin\docs\review\sample-cv.md" "D:\dev resu-studio\Alex Morgan CV.md"
Copy-Item "D:\resu-plugin\docs\review\sample-job-ad.md" "D:\dev resu-studio\job ad.md"
```

This copies the skill the same way `npx skills add` would install it, but from this branch.  
(`npx skills add` normally installs from `main`, which may differ from this branch.) Claude Code
looks in `.claude\skills` rather than `.agents\skills`; if you use Claude Code, run the first  
two lines again with `.claude` in place of `.agents`.

### 2\. Open the test folder

**File > Open Folder**, choose `D:\dev resu-studio`. Start your AI tool's chat in that window.

### 3\. Talk to it like a person would

Say something like:

> I want to apply for a job. My CV is "Alex Morgan CV.md" and the ad is "job ad.md".

### 4\. What you should see, in order

Tick these off as they happen:

*   **It finds your Python on its own.** It should run the finder and use the
    returned interpreter without asking you where Python is.
*   **It asks where to keep your files before doing anything else.** It should offer  
    `D:\dev resu-studio\Resu - CV Builder` or a folder in your home folder.
*   **It tells you about older work it found.** If an older data folder exists, it
    should be listed with counts only. For this test, say **no, don't bring it in**.
    It must not use any real application data.
*   After you choose, `D:\dev resu-studio\Resu - CV Builder` exists, with `1 About me`,  
    `2 My record`, `3 Jobs`, `4 Finished documents`, a `README.txt` and a `.gitignore`.
*   It starts a **job** for the ad and names it (role and employer).
*   It asks **how deep to score** before scoring.
*   The **Studio** it hands you is in `4 Finished documents\<Employer> - <Role>\`.
*   **Resu Desk** is in `4 Finished documents\Resu Desk.html` and shows the job.

For the writing-mode workflow:

*   The Studio opens on **Writing**, with the guiding brief and distinct versions of
    the same original profile and experience bullet.
*   **Create my own mode** prepares samples only. Saving a reusable preference is
    explicit, and a refinement updates the existing personal option.
*   **Use this mode and rewrite my CV** makes one handoff. After receiving it, the
    AI names the selected mode and generates suggestions without another permission question.
*   Accept, reject and manually edit different suggestions. Switch modes and return:
    matching saved rounds are reused, and manual wording and keep decisions survive.
*   A changed suggestion does not inherit approval of different wording.
*   After assembly, confirm the Studio and final PDF contain the accepted text,
    all sections and correct role/date associations. Check the extracted PDF text too.

Then add a second job. Paste any other job ad text (a made-up one is fine) and say:

> Here's another job I want to apply for.

*   It starts a **second job** and says the first one is kept as it is. Nothing is replaced.
*   Resu Desk now shows **both** jobs.
*   On the Desk, change the second job's stage to **Applied**, press **hand to AI**, copy  
    the text and paste it into the chat. It should write the change and hand you an updated  
    Desk showing Applied.

### 5\. Check git cannot see the private files (optional)

In a terminal in `D:\dev resu-studio`:

```
git init
git status
```

`Resu - CV Builder` must **not** appear in the list. The `.agents` folder and the two sample  
files will; that is expected.

### 6\. Clean up

1.  Delete the folder `D:\dev resu-studio`.
2.  Open `%USERPROFILE%\.resu-studio\locations.json` in VS Code and delete the entry for
    `d:\dev resu-studio` (or leave it; it does nothing once the folder is gone).

Nothing else was created anywhere.

---

## If something looks wrong

Copy what the assistant said, and what you expected from the checklist, into a chat on  
this branch. Screenshots help. Say which AI tool you used, because Claude Code, Codex and  
Copilot look for skills in slightly different folders.
