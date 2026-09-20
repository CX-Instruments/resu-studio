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
`/home/<you>/mnt/<folder>`. `paths.py` looks for a mounted folder with the same name and
says which one it found, so read the message rather than guessing at a path.

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

**Open the studio as a file.** It is a complete HTML page with nothing to install. Say
where it is, and offer to open it in their browser if you can.

## In a chat that cannot run anything

Say so once, plainly, before Phase 3: the scoring, the proposals and the letter can
all be done in the conversation, and the studio and the PDF cannot be made here. Then do
the parts that can be done, write the CV out as markdown in the chat, and do not
pretend a file was written.

## The person's folder

**The person chooses their folder, once per install, and it is never guessed.** A skill
can be installed in more than one place on one computer: inside a project, the way
`npx skills add` puts it in `<project>/.agents/skills/`, or for the whole computer. Each
install asks separately, because a person who installed it inside one project does not
expect it to open an application they started somewhere else.

**First, `python3 scripts/paths.py --status`.** It says whether this install has a folder,
which folders to offer, and every folder on the computer that already holds Resu Studio
work, with counts of what is in each. It never prints anybody's CV.

- **Chosen:** carry on.
- **NOT CHOSEN YET:** every script that needs the folder stops, with exit code 6 and one
  sentence, until it is chosen. Nothing is created and no other folder is used meanwhile.
  Say to the person, in plain words, what `--status` found and offered, and ask:
  - where their files should live: inside this project (`<project>/Resu - CV Builder`),
    in their home folder (`~/Resu - CV Builder`), or a folder they name;
  - for any older work it listed, whether to bring it in. Say where it is and what it holds.

  Then run their answer, and say the folder's name back to them:

```bash
python3 scripts/paths.py --choose project
python3 scripts/paths.py --choose home --bring "<the older folder they agreed to>"
python3 scripts/paths.py --choose "<a whole folder path>"
```

`--choose` records the choice in `~/.resu-studio/locations.json`, outside every install, so
an update cannot lose it. `--bring` copies an older folder in, in either layout: nothing
there is moved or deleted, nothing already in the new folder is written over, the documents
list is pointed at the copies, and anything that is not Resu Studio's is left behind and
named. Loose working files from before jobs had folders wait in `.resu/from-before-jobs/`
for `jobs.py adopt`.

**What is in the folder:**

```
Resu - CV Builder/
  README.txt             says the folder is private
  .gitignore             one line, *, so git ignores everything in the folder
  1 About me/            the CV as it arrived, the CV as markdown, links.md
  2 My record/           facts.md, answers.md
  3 Jobs/<job id>/       job.json, ad/, asks.md, scorecard.md, proposals.md, ...
  4 Finished documents/  Resu Desk.html, and one folder of documents per job
  .resu/                 documents.json and the scripts' own notes
```

**Private by default.** The `.gitignore` inside the folder keeps all of it out of any git
repository the folder sits in, without anybody's own `.gitignore` being edited. Never
remove it, never copy anything out of this folder into the project around it, and never
commit a CV, a ledger or a document anywhere.

**Two things choose without asking, and `--status` says so.** A `data-location.txt` beside
`SKILL.md`, one line holding a folder, written for this install. And a host's own data
folder, `CLAUDE_PLUGIN_DATA` in Claude or `PLUGIN_DATA` where the Agent Plugins standard sets
one. The old `~/.resu-studio/location` pointer and a plain `~/.resu-studio` are no longer used
on their own: `--status` lists them as older work to bring in.

**`--pdf-dir` moves rendered output and nothing else.** It does not relocate `facts.md`,
`answers.md` or the CV as it arrived.

## Commands

**Never send them a command to run.** The studio prints one for the design they land
on, and that is for you to execute, not for them.

**Run every command from this skill's own folder**, the one holding `SKILL.md`. Every
command names `scripts/...` relative to it.

**Every command that names a file uses `paths.py` to name it.** A bare relative
`facts.md` resolves against the working directory, which in a cloud session is thrown
away at the end of the session, so the file the next advertisement needs is gone. Write
it as command substitution, every time:

```bash
python3 scripts/paths.py --facts                  # one bare path, nothing else
python3 scripts/paths.py --answers
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
& $PY scripts/build_studio.py --cv "$(& $PY scripts/paths.py --about)/<their CV>.md" `
    --scorecard "$J/scorecard.md" --job <job id>
```


Writing state belongs to each job: `writing.json` and immutable `.writing` revisions/source snapshots. Inputs, reviews, handoffs and proposal rounds stay there too. Reusable personal modes belong in `2 My record/writing-modes`; only generic built-ins ship with the skill. See `writing-engine.md`.
