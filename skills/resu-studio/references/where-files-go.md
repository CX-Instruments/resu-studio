# Where the work happens, and where the files go

SKILL.md carries the short version. This is the whole of it. Read it the first time in a
conversation that a script is about to run or a file is about to be handed over.

## First, work out where you are running

This skill is installed in more than one kind of place, and what "hand the file over"
means depends on which one this is. Look at what you can actually do, not at what you
are called.

- **A temporary cloud session.** Claude's Cowork and claude.ai, and any other host
  that runs code in a sandbox of its own. The session has its own disk, which is
  thrown away when the conversation ends, and often a Chromium-family browser. The
  person's own computer is somewhere else.
- **The person's own computer.** Codex, GitHub Copilot, Cursor, Gemini CLI and Claude
  Code all run commands on the machine in front of the person. The disk is theirs and
  it stays. Whether a browser is there depends on the machine: most have Chrome or
  Edge, and `to_pdf.py` looks for both.
- **A chat with no way to run anything.** Some chat apps load the instructions and
  cannot run a script at all.

## In a temporary cloud session

**Run every script in your own session, not on the person's computer.** The scripts
need a Chromium-family browser to print the PDF, and the session usually has one. A
person's machine may not, and a non-technical person should never be asked to install
anything, set a path, or type a command. They should not have to know that any of this
is Python.

**Then hand the finished files over. Every time.** The session is temporary. A CV
written there and not delivered is gone when the session ends, and the person will not
know that happened until they go looking. So:

- deliver each finished document into the conversation, as a file they can open, and
- write it into a folder on their own computer when one is connected, and say which
  folder and what it is called, in plain words.

**If they have a folder connected, point at it, so their record sits on their own
disk.** Write the path as this session sees it. A Windows path like
`D:\Users\you\CVs`, or any path with a backslash in it, or a relative path, is refused
here with a plain message rather than quietly building a folder whose name contains the
backslashes. A person on Windows has their folders mounted somewhere under a session
path that starts with `/` and has no drive letter, usually something like
`/home/<you>/mnt/<folder>`. Use only the actual current task workspace or an explicitly named destination. Do not search mounts for a folder with a similar name. If the supplied path is unavailable, explain the blocker and ask for the accessible path.

## On the person's own computer

**Run the scripts where you are.** The files you write are already on their disk, so
there is nothing to upload and nothing to lose when the conversation ends. Tell them the
folder and the file name in plain words, the same as anywhere else.

**Check the two things the scripts need, once, before the first script.** Python 3.8 or
newer, and a Chromium-family browser for the PDF.

**Find Python with the finder, not by guessing.** `python3 --version` and `python --version`
are not a test on Windows: `python3` is usually missing, `python` is often the Microsoft
Store placeholder that prints a message instead of running, and Anaconda or Miniconda
installs are left off the PATH by their own installer. People have had to tell an assistant
where their Python was, every conversation. Run the finder instead:

- PowerShell on Windows: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\find_python.ps1`
- bash, zsh or Git Bash: `sh scripts/find_python.sh`

It tries, in order: `RESU_PYTHON` if set, the path it found last time, an active conda
environment (`CONDA_PREFIX`, `CONDA_EXE`), the Anaconda, Miniconda, Miniforge and
Mambaforge folders under the user folder, `AppData\Local`, `ProgramData` and the drive root,
the `py` launcher, python.org installs, Homebrew and `/usr/bin`, and last whatever the PATH
calls `python3` or `python`. Each is run and kept only if it really is Python 3.8 or newer.
The last line it prints is the full path. Use that path, quoted, in place of `python3` in
every command from then on, and do not ask the person about Python while it is working.
The path is remembered in `~/.resu-studio/python.txt` and checked again before it is used.

If it exits 1, nothing usable was found anywhere it looked. Say so plainly, say what Python
is needed for, and ask whether they have one somewhere unusual; if so, set `RESU_PYTHON` to
its full path and run the finder again. If there is no browser, `--pdf` says
so in one sentence; say that sentence to them and offer the studio, which prints from
their own browser with **Save as PDF**. If there is no Python at all, say so plainly and
say what it is needed for. Do not install anything without asking.

**A Windows path is the right path on Windows.** When the scripts run on Windows itself,
`D:\CVs` is accepted as written. The refusal above is only for a Linux or Mac session
that cannot see a drive letter.

**Hand over both HTML links.** It is a complete HTML page with nothing to install.
Follow `studio.md`, "Open and hand over": use the exact generated Studio and Resu Desk
paths, attempt one Studio launch through `open_studio.py` on the user's computer,
and refresh the existing tab after rebuilds. Always include both links in the reply.

## In a chat that cannot run anything

Say so once, plainly, before Phase 3: the scoring, the proposals and the letter can
all be done in the conversation, and the studio and the PDF cannot be made here. Then do
the parts that can be done, write the CV out as markdown in the chat, and do not
pretend a file was written.

## The person's folder

**Default: `<current task workspace>/Resu - CV Builder`.** The task workspace is the
folder where the user started this task, regardless of where the plugin is installed.
Never select it from an old install setting, global registry, host data environment
variable, nearby CV location or previous conversation. `--status` reports the location
without scanning for older work. `--choose project` initialises the default. Neither
needs a new folder-choice question.

The fixed layout is:

```
Resu - CV Builder/
  README.txt             explains the private folder
  .gitignore             ignores its contents
  1 About me/            supplied originals and links
  2 My record/           optional saved history and personal modes
  3 Jobs/<job id>/       source CV, facts.md, answers.md, ad/, asks.md, working files
  4 Finished documents/  Resu Desk.html and each job's documents
  .resu/                 internal metadata
```

**Different locations and imports require explicit user instructions.** Only when the
user actually asks, pass their instruction verbatim with the destination they named:

```bash
python3 scripts/paths.py --choose "<absolute destination>" --user-instruction "<their explicit request>"
python3 scripts/paths.py --choose project --bring "<explicitly requested older folder>" --user-instruction "<their explicit import request>"
```

Never manufacture that instruction from "start fresh", "don't use old outputs", an
old setting or your own plan. An alternative destination is recorded only in this
workspace's `Resu - CV Builder/.resu/location.json`. That choice does not affect any
other workspace. `--choose project` resets this local override; it leaves old data in
place. Import copies without overwriting or deleting the source. Do not run it merely
because an older folder exists.

**Fresh work keeps the standard destination.** Do not create sibling roots with New,
Fresh, year or other suffixes. New applications use `jobs.py new`; an explicit separate
fresh application for an existing role uses `--again`. Resume only when requested.
Read only this application's supplied or explicitly designated evidence. Existing
outputs and `2 My record` are not automatic inputs. If an older application is explicitly
resumed, copy its authorised facts/answers into its job folder before using it.

Keep generated scripts, temporary files and intermediate outputs inside the active job
folder. Keep finished files inside `4 Finished documents`. An output override such as
`--pdf-dir` does not authorise a destination outside this root: that requires the user's
explicit instruction too. Never delete old work to make room for a fresh run.

The folder's `.gitignore` keeps private data out of the surrounding repository. Do not
remove it or commit personal sources, ledgers or outputs. If the default or its internal
folders redirect outside the root, or the workspace cannot be resolved, explain the
blocker instead of searching elsewhere or inventing another destination.

## Commands

**Never send them a command to run.** The studio prints one for the design they land
on, and that is for you to execute, not for them.

**Before changing directories, capture the real task workspace:** PowerShell `$env:RESU_WORKSPACE = (Get-Location).Path`, or bash `export RESU_WORKSPACE="$PWD"`. Keep that value throughout the task. Then the relative `scripts/...` examples can run from the skill folder. Alternatively stay in the workspace and use absolute script paths. Never set the workspace to the plugin/cache folder.

**Every command that names a file uses `paths.py` to name it.** A bare relative
`facts.md` resolves against the working directory, which in a cloud session is thrown
away at the end of the session, so the application file is misplaced. Write
it as command substitution, every time:

```bash
python3 scripts/paths.py --job <job id> --facts                  # one bare path, nothing else
python3 scripts/paths.py --job <job id> --answers
python3 scripts/paths.py --about                  # 1 About me
python3 scripts/paths.py --jobs                   # 3 Jobs
python3 scripts/paths.py --documents              # 4 Finished documents
python3 scripts/paths.py --job <job id>               # that job's own folder
python3 scripts/paths.py --job <job id> --job-ad      # where its advertisement goes
python3 scripts/paths.py --job <job id> --job-documents
```

**The commands in this skill are written for bash.** In PowerShell, the same thing is
written with PowerShell's own variables, and Python is the path the finder printed, called
with `&`:

```powershell
$PY = powershell -NoProfile -ExecutionPolicy Bypass -File scripts\find_python.ps1
$J = & $PY scripts/paths.py --job <job id>
& $PY scripts/build_studio.py --cv "$(& $PY scripts/paths.py --job <job id>)/<their CV>.md" `
    --scorecard "$J/scorecard.md" --job <job id>
```


Writing state belongs to each job: `writing.json` and immutable `.writing` revisions/source snapshots. Inputs, reviews, handoffs and proposal rounds stay there too. Reusable personal modes belong in `2 My record/writing-modes`; only generic built-ins ship with the skill. See `writing-engine.md`.
