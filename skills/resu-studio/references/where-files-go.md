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

**Check the two things the scripts need, once, before Phase 3.** Python 3, and a
Chromium-family browser for the PDF. Run `python3 --version`; on Windows, where
`python3` is usually missing, try `python --version` and then `py --version`, and use
whichever answers in every command from then on. If there is no browser, `--pdf` says
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

**Their folder is `~/.resu-studio`, unless somebody named another one.** That is
outside the plugin, so a plugin update cannot delete it, and it is where `facts.md`,
`answers.md`, `cv-source/` and `_Your Documents Are Here/` all live. Run
`python3 scripts/paths.py` to see the folder and why it was chosen. Nothing about this
needs setting up: the default already survives an update.

To choose another folder, write one line, the folder, in either pointer file:

- `~/.resu-studio/location` is the stable one, outside the plugin.
- `data-location.txt` beside `SKILL.md` still works and is copied out to the stable
  one the first time it is used, so the next update cannot lose the pointer.

A pointer beats the host's own data folder (`CLAUDE_PLUGIN_DATA` in Claude,
`PLUGIN_DATA` where the Agent Plugins standard sets one), because a person writing a
path has said what they want and a host guessing one has not.

**`--pdf-dir` moves rendered output and nothing else.** It does not relocate
`facts.md`, `answers.md` or the CV as it arrived. Those follow the pointer.

**Anything left in the old in-plugin folder is copied out on the first run.** The old
folder is left exactly as it was. Nothing already in the new folder is written over,
and the run says on screen what it did and what it left alone. It happens once. If the
person sees that message, it is their own history being brought somewhere an update
cannot reach.

## Commands

**Never send them a command to run.** The studio prints one for the design they land
on, and that is for you to execute, not for them.

**Run every command from this skill's own folder**, the one holding `SKILL.md`. Every
command names `scripts/...` relative to it.

**Every command that names a ledger uses `paths.py` to name it.** A bare relative
`facts.md` resolves against the working directory, which in a cloud session is thrown
away at the end of the session, so the file the next advertisement needs is gone. Write
it as command substitution, every time:

```bash
python3 scripts/paths.py --facts       # one bare path, nothing else
python3 scripts/paths.py --data        # the folder the ledgers live in
python3 scripts/paths.py --answers
python3 scripts/paths.py --cv-source
python3 scripts/paths.py --documents
```

**The commands in this skill are written for bash.** In PowerShell, the same thing is
written with PowerShell's own variables, and the Python command is whichever one
answered above:

```powershell
$D = python scripts/paths.py --data
python scripts/build_studio.py --cv "$(python scripts/paths.py --cv-source)/<their CV>.md" `
    --scorecard "$D/scorecard.md" --role "<the job title>"
```
