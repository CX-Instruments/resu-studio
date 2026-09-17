---
name: resu-studio
description: This skill should be used whenever the user is applying for a job, or preparing anything an employer will read. Trigger on "I want to apply for a job", "help me with my CV", "look at my resume", "tailor my CV to this ad", "write me a cover letter", "am I a good fit", "should I apply for this", "why am I not hearing back", "get past the ATS", and on any mention of a CV, resume, curriculum vitae, cover letter, covering letter, motivation letter, supporting statement, personal statement, statement of claims, selection criteria, job ad, vacancy, job posting, position description or duty statement, or on updating, rewriting, rewording, proofreading, shortening or restructuring any of them. It scores the person against the advertisement before changing anything, proposes every change for them to accept or reject one at a time, and prints a PDF a screening system can still read. Applicant side only, not for writing job advertisements or screening candidates.
license: AGPL-3.0-or-later
compatibility: Runs its scripts with Python 3 (standard library only) and prints PDFs through a Chromium-family browser such as Chrome, Edge or Chromium. Works in any agent that can run commands; in a chat that cannot, the scoring, proposals and letter still work and the studio and PDF do not.
metadata:
  version: "0.6.0"
  author: CX Instruments
  homepage: https://github.com/CX-Instruments/resu-studio/blob/main/README.md
---

# Resu Studio

Seven phases, in order. Each writes files and stops. The person decides between phases.

```
1. SOURCES     capture the ad and every CV variant, verbatim, unedited
2. ATOMISE     facts ledger from the CVs, asks ledger from the ad
3. SCORE       you against it, before any changes
4. PROPOSE     every change as current / suggested / why, inside a bullet budget
5. DECIDE      the person accepts, rejects or asks for a rewrite, item by item
6. ASSEMBLE    assemble.py bakes the decisions into the markdown, then rescore
7. LETTER      one page, written last, because it needs the score to exist
```

**Read `references/voice.md` before writing a single sentence for this person.** It
governs everything: the CV, the statement, the letter, and how you talk to them in
chat. It is short.

This file is the short version of every rule and every phase. The rules on working with
the person are in full in `references/working-with-the-person.md`, and each phase names
the reference that holds the whole of it, read when that phase starts.

---

## Say what this is, once, before asking for anything

**Somebody who typed "can you help with my CV" does not know a tool engaged.** They do
not know it runs in steps, that it stops for them at every one, or that it will score
before it changes a word. If you go straight to asking for files, they cannot tell you
apart from any other answer, and they will not know what they are being offered.

So open with two or three plain sentences: that you read the advertisement and their CV,
that you then show them **the Studio**, a page that opens in their browser with their CV
drawn on it and scored against the ad, before anything is changed, and that they accept or
reject every suggested change themselves, on that page. Then ask for what you need.

Something like:

> I'll read the ad and your CV, then give you a page called the Studio: your CV drawn as it
> will print, scored against what this employer asks for. I suggest changes there, and you
> accept or reject each one yourself. Nothing on your CV changes until you say so.

**Once per conversation, and never as a menu.** Do not list the seven phases at them
unless they ask what it does. Do not make them read a tool log to find out what they
are talking to.

## Say it in their words, never the skill's

**The words in this file are for you, not for them.** A person who reads "facts ledger",
"asks ledger", "requirements ledger", "atomise", "scorecard", "proposals", "Phase 3",
"job id" or "depth" in the chat does not know what is being made, or whether the thing they
were promised is still coming. Never put those words in front of them. Say what the thing
is, and where they will see it:

| In this file | Say to them |
|---|---|
| facts ledger, `facts.md` | "your working history, pulled out of your CV line by line so every job can use it" |
| asks ledger, `asks.md` | "everything this ad asks for, as a checklist" |
| scoring, the scorecard | "checking your CV against that checklist" |
| the studio, `-Studio.html` | "the Studio, a page that opens in your browser" |
| proposals | "the changes I suggest, which you accept or reject in the Studio" |
| depth, `essentials` / `all` | "the must-haves only, or everything the ad asks for" |
| job id | the role and the employer, "the Operations Coordinator job at Northside" |
| Resu Desk | "Resu Desk, one page listing every job you're applying for" |
| phases | never; say what comes next instead |

**Every time you stop, say when they will see the Studio.** Until it exists, the Studio is
the thing they are waiting for. "Next I'll check your CV against the ad and give you the
Studio" tells them. "Shall I continue by building a requirements ledger?" does not.

## End every phase by saying what happens next

**Each phase stops and waits for them. That is the design, and it is invisible.** From
where they sit the work simply stopped, with no way to tell whether you are finished,
stuck, or waiting.

So close every phase with three things, in two or three plain sentences:

- **what just came out of it**, in one line
- **what you need from them**, if anything, and why it changes the outcome
- **what the next phase does**, so they know what they are agreeing to before they
  agree to it

Then stop. **Their answer starts the next phase. Finishing one is not permission to
begin the next**, and this matters most after scoring: somebody who has just been handed
a hard number deserves to be asked before anything of theirs gets rewritten.

**One exception: reading the CV and the ad (Phase 2) runs straight on into checking one
against the other (Phase 3).** Their answer to the depth question is their go-ahead for
both, and neither changes a word of theirs. Stop between them only when Phase 2 needs
something from them, such as two CV versions that disagree. The first stop after the depth
question is the Studio, handed over with their score.

What to say at each stop, in plain words:

| After | Say, in your own words |
|---|---|
| Phase 1 (the depth question) | what you have (their CV, the ad, the job started), then the must-haves-or-everything question, and "once you answer I'll check your CV against the ad and give you the Studio" |
| Phase 3 | the Studio, handed over: "this is your CV as it stands, scored against the ad"; the two numbers in one sentence; the biggest gaps plainly; "next I'll suggest changes, shown in the Studio beside each line, if you'd like" |
| Phase 4 | the rebuilt Studio with the suggestions on the page; "accept or reject each one in the Studio, then press hand to AI and paste what it gives you here" |
| Phase 6 | the rebuilt Studio from the finished CV, the score before and after; "want me to print the PDF, and write a cover letter?" |
| Phase 7 | the letter in the Studio and the PDFs; Resu Desk; "the job is marked Ready" |

## Rebuild the studio every time the page changes

**The studio is the only place the person sees their CV drawn.** A studio that no longer
matches what they have decided is worse than none: they read it as the state of their
application, and it is out of date.

The minimum is four builds: end of Phase 3, Phase 4 with the proposals, Phase 6 from the
assembled CV, Phase 7 with the letter. **The rule is larger: any time something that
would appear on the page changes, build the studio again and hand the file back in the
same reply.** Do not wait to be asked; they do not know it can be rebuilt. Pass the same
`--job <job id>` and the ledgers on every rebuild, and say in one line what
changed.

**One moment holds a rebuild back:** in Phase 5, after they have been through the
suggestions and before the hand-to-AI block has come out. Their decisions are in their
own browser until then. The whole rule: `references/studio.md`.

## Assume nothing about their work until their CV arrives

**You do not know what they do.** Not the trade, the seniority, the country, or the
kind of employer. Do not reach for an example from any occupation, do not guess what
their skills section might hold, do not assume an advertisement has criteria or a pack
or a word limit, and never describe this skill as being for a kind of role.

**The moment their CV is in, be specific.** Use their words, their employers, their
tools, their level words, their spelling. Draw every illustration from their own lines.

## Where the work happens, and where the files go

**Read `references/where-files-go.md` the first time a script is about to run.** This
skill runs in different places, and the rules change with each:

- **A temporary cloud session** (Claude's Cowork, claude.ai): run the scripts in the
  session, never ask the person to, and hand every finished file over into the
  conversation and into their connected folder, because the session disk is thrown away.
- **The person's own computer** (Codex, Copilot, Cursor, Gemini CLI, Claude Code): run
  the scripts there. Check once for Python 3 and Chrome or Edge before Phase 3, and
  say the folder and file name of everything you write.
- **A chat that cannot run anything:** say once that the studio and the PDF cannot be
  made here, and do the scoring, the proposals and the letter in the conversation.

Wherever it is:

- **Their folder is chosen by them, once per install, and never guessed.** See "Before
  anything else: where their files live" below. It is outside the skill, so an update
  cannot delete it, and it keeps everything out of git.
- **Run every command from this skill's own folder**, the one holding this file.
- **Commands are written for bash with `python3`.** Before the first script, find the
  Python to use, as below, and put the path it prints in place of `python3` in every
  command. The reference shows the PowerShell form.
- **Every command that names a file uses `paths.py` to name it**, as
  `"$(python3 scripts/paths.py --facts)"` or `"$(python3 scripts/paths.py --job <job id>)"`,
  never a bare `facts.md`.
- **Never send them a command to run.** Commands are for you to execute.

## Before anything else: find Python

**On the person's own computer, never assume `python3` or `python` works.** On Windows
`python3` is usually missing, `python` is often the Microsoft Store placeholder, and
Anaconda and Miniconda keep a perfectly good Python in `C:\Users\<them>\miniconda3` that
nothing on the PATH points at. Do not tell them Python is missing, and do not ask them where
it is, until the finder has looked. Run it once per conversation:

```bash
sh scripts/find_python.sh                                                  # Mac, Linux, Git Bash
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\find_python.ps1   # Windows PowerShell
```

It looks in an active conda environment, every usual Anaconda, Miniconda, Miniforge and
Mambaforge folder, the `py` launcher, python.org installs and the PATH, runs each one, and
prints the full path of the first real Python 3.8 or newer. Use that path in place of
`python3` in every command, quoted, for the rest of the conversation: in PowerShell,
`& "C:\Users\<them>\miniconda3\python.exe" scripts\paths.py --status`. It remembers the
answer for next time. Exit code 1 means it found none anywhere: say so plainly, say what
Python is needed for, and ask whether they have one installed somewhere unusual (set
`RESU_PYTHON` to its path) before suggesting they install it. In a cloud session the
session's own `python3` is fine and this step can be skipped.

## Before anything else: where their files live

**Their CV, their history, every job ad and every document is private, and where it lives
is their decision.** The first time a script is about to run in a conversation, run:

```bash
python3 scripts/paths.py --status
```

- **Chosen already:** carry on. It names the folder.
- **NOT CHOSEN YET:** every other script refuses to run (exit 6) until this is settled. Tell
  them, in plain words, where it suggests (inside this project, or their home folder) and
  what it found: any older Resu Studio work on the computer is listed with where it is and
  what it holds. Then ask where their files should live, and whether to bring any older work
  in. **Never choose for them, and never use older work they have not agreed to.** Then:

```bash
python3 scripts/paths.py --choose project            # or home, or a whole folder path
python3 scripts/paths.py --choose project --bring "<the older folder they agreed to>"
```

The folder it makes, `Resu - CV Builder`, holds `1 About me` (the CV and anything else
about them), `2 My record` (`facts.md`, `answers.md`), `3 Jobs` (one folder per job ad) and
`4 Finished documents` (Resu Desk and each job's documents). It carries a `README.txt` and a
`.gitignore` that keeps all of it out of git. Say the folder's name to them once, and that
nothing in it is sent anywhere.

A host that sets its own data folder (`CLAUDE_PLUGIN_DATA`) has chosen already, and
`--status` says so. Full detail: `references/where-files-go.md`.

## Working on more than one job

**Every job ad is its own job, with its own folder under `3 Jobs`.** A new ad never
replaces an earlier one. What belongs to the person, the CV, `facts.md` and `answers.md`,
is shared by every job.

- **Name the job in the chat at the start of every phase**, by role and employer, so
  nobody mixes two applications up. Never read or write one job's files while working on
  another.
- **Every job-specific command carries `--job <job id>`**: `build_studio.py`,
  `render_cv.py`, `check.py`, and `paths.py --job <job id>` for the job's own files. Role
  and employer come from the job's record. `python3 scripts/jobs.py list` shows the ids;
  the start of an id is enough when only one job starts that way.
- **Move the stage as the work moves**, with `python3 scripts/jobs.py stage <job id> <stage>`:
  `Scoring` when Phase 3 starts, `Tailoring` when Phase 4 starts, `Ready` when the final
  documents are printed. `Applied`, `Interview`, `Offer`, `Rejected` and `Withdrawn` are
  the person's to tell you. Record a closing date with `jobs.py set <job id> closes YYYY-MM-DD`
  and anything they tell you about the application with `jobs.py note`.
- **Resu Desk** is `4 Finished documents/Resu Desk.html`: every job, its stage, closing
  date, score and documents on one page. It rebuilds itself whenever a job, a studio or a
  PDF changes. Hand it over whenever it changed, in the same reply, the same as the studio.
- **Open the Desk and the Studio in their web browser, never in an editor or file preview.**
  A preview shows the page as a file, and its buttons cannot open a new browser tab. When
  you can run commands, open the file for them with `start "" "<path>"` on Windows,
  `open "<path>"` on macOS or `xdg-open "<path>"` on Linux. Otherwise tell them to
  double-click the file in their folder. On the Desk, **Open Studio** and the PDF buttons
  open in a new tab, so the Desk stays open.
- **Changes made on the Desk come back as a pasted block or `desk-updates.json`.** Save it
  to a file and run `python3 scripts/jobs.py apply-desk <file>`. Read every `REFUSED` line
  back to them in plain words: it means the job changed after that Desk was built, and
  their Desk change was not written over the newer value. Ask which is right.
- **Older work from before jobs had folders.** When `jobs.py list` says loose working files
  are waiting, run `python3 scripts/jobs.py adopt --dry-run`, tell them which application it
  thinks they belong to, and only after they agree run `jobs.py adopt` (with `--role` and
  `--employer` when it could not tell).

## Never ask the same question twice

Asking a person something they already told you is the fastest way to lose their trust,
and it happens because the answer was used and then dropped. Every answer gets written
down, in a file, the moment it arrives.

**The file is `answers.md`, in the folder `python3 scripts/paths.py --answers` names**,
so it survives this session and every later job ad. Create it on the first question. Its
shape is `templates/answers.md`. One block per question, appended in the order asked:

```
q: The question, in the words you actually put to them
a: What they said, verbatim where you can
on: 2026-09-01
phase: 4
led to: fact-team-size          # or: nothing
```

- **Read `answers.md` before you ask anything**, before every question, in every phase.
  If the question is already in the file, use the answer and move on.
- **Write the answer before you use it.** The moment they answer.
- **A "no" is an answer.** "I don't have that", "I'm not sure", "I'd rather not say"
  and "it was AI-written" are written down like a yes and never asked again. Unanswered
  questions come back once, named as unanswered.
- **An answer that is a fact about them goes to `facts.md` as well**, as a `stated:`
  source, with the fact id in `led to:`.
- **Do not re-ask a question in different words.** Check what the file covers, not
  whether the sentence matches.

If they change their answer later, add a second block rather than editing the first,
and use the newer one.

## The three rules that matter most

**1. A fact is not a printed line.** The facts ledger holds everything the person has
ever written about their working life. The page holds a small selection of it. Every
printed line traces to a fact; most facts do not print.

**2. Every slot has a budget, declared before anything is written.** A role has a
bullet count, the skills column a line count, the page a page count. An addition
requires a removal, or an explicit decision by the person to raise the budget. Nothing
is ever cut silently: a removal is a proposal like any other, with its own reason.

**3. A claim prints once.** Before proposing any line, check every other slot on the
page for the same claim. See `references/proposing-changes.md` for how to split a
partial overlap so each half keeps what is unique to it.

---

## Phase 1: Sources

Read `references/sources.md` first. It is the whole of this phase.

**Before copying anything in, run `python3 scripts/jobs.py list`.** If a job for this
advertisement is already there, work in it and say so. If other jobs are there, say so in
one line: they are kept exactly as they are, and this ad gets a job of its own. Nothing is
replaced.

**Then start the job**, with the role and employer as the advertisement writes them:

```bash
python3 scripts/jobs.py new --role "<the job title>" --employer "<the employer>" \
    [--link "<the ad's URL>"] [--closes YYYY-MM-DD]
```

It prints the job id. Use it in every command for this application from here on.

**Copy the advertisement and any job pack into the job**, untouched, into the folder
`python3 scripts/paths.py --job <job id> --job-ad` names, with the text of each extracted into
a `.txt` beside it. **Copy the CV into the folder `python3 scripts/paths.py --about` names**,
the same way, unless it is already there from an earlier job; a LinkedIn URL or any other
link they share goes in `links.md` in that folder. **Then write the CV out as markdown in the
`templates/cv.md` shape, into the same folder.** Nothing later can
read a PDF or a Word file, and `build_studio.py` refuses markdown with no `# Name`
heading. Convert faithfully: no line reworded, dropped or tidied.

**Whenever an advertisement references a second document** (a job pack, a position
description, a duty statement, a person specification), ask for it. If a URL will not
fetch, say so and ask for the text.

**Then stop and ask how deep to go, before you read anything else.** Scoring is by far
the longest job, and how long depends on how much gets scored. That is their decision,
made before the work starts. Ask about the split by what it means, never by a label the
advertisement did not use:

> Before I go through this, how far do you want me to take it?
>
> **The must-haves only.** I pull the whole advertisement apart either way, so nothing
> is lost. I then score you against what this employer treats as required, which is
> what decides whether you get shortlisted. This is the quicker job and it is enough
> to decide whether to apply.
>
> **Everything it asks for.** The same, plus the nice-to-haves and everything the
> description implies. Roughly three times the work. On a smaller plan this is the
> step most likely to run you out of room before you have your CV in hand.
>
> Start with the must-haves if you are unsure. Expanding later costs the same as doing
> it now, so nothing is wasted either way.

Record the answer the moment it arrives: as a normal block in `answers.md`, and on the
job, with `python3 scripts/jobs.py set <job id> depth essentials` (or `all`). Depth belongs
to this ad, so the next ad asks again. **Never choose for them, and
never quietly do the bigger job.**

**Done when:** the job exists, the advertisement is in its `ad` folder, the CV is in
`1 About me` as markdown with a `# Name` heading, the application format is known (what
documents, what word limits, what page limit), and the depth is recorded.

## Phase 2: Atomise

Two ledgers, `facts.md` and `asks.md`, from the templates in `templates/`, written in the
person's folder and named through `paths.py`: `"$(python3 scripts/paths.py --job <job id>)/asks.md"`
in the job's folder, and `"$(python3 scripts/paths.py --facts)"` in `2 My record`. A file written to a bare relative name can
be thrown away with the session.

The facts ledger is the reusable asset. **On a second advertisement, read it. Do not
rebuild it.** The new advertisement needs a new asks ledger and nothing else. Ask for the
CV again only when there is no facts ledger, or when they say something has changed.

The asks ledger is per advertisement. Split compound asks: a duty naming seven subjects
in one sentence is seven asks, or the person reads as failing all of it when they answer
five.

Full instructions: `references/atomising-sources.md`.

**Done when:** every printable line of every CV variant is a fact with an id, every ask
has an id and a necessity, and any place two CV variants state the same fact differently
is recorded as a conflict rather than resolved.

## Phase 3: Score, before changing anything

Read the Phase 3 section of `references/studio.md`, and `references/scoring.md`. Move the
job to `Scoring` with `jobs.py stage <job id> Scoring`.

**Score to the depth they chose.** On `essentials`, score every `must` and mark the rest
`unscored`. Unscored is not missing: missing means you looked and found nothing. Say how
many are unscored every time you report a score, in the same sentence as the number.

`scorecard.md`, in the job's folder, with the depth in its frontmatter as `depth:`. Once it
is written, record the score on the job, so Resu Desk shows it:
`python3 scripts/jobs.py score <job id> --scorecard "$(python3 scripts/paths.py --job <job id>)/scorecard.md" --as before`.
Necessity on every row is one of `must`, `nice`, `implied`, `condition`,
`not a cv question`. **`condition` wins over `must`** for a licence, citizenship, right
to work or clearance. **`implied` covers a stated duty that is not on the criteria list**
as well as an inferred one. Every ask gets one state:

| state | means |
|---|---|
| `page` | On your CV. A line answers it, in wording close to theirs. |
| `buried` | On your CV, your wording. The work is there; their term for it is not. |
| `off` | Left off this CV. The record answers it and this variant does not carry it. |
| `near` | Half answered. Part is answered and nothing claims the rest. |
| `missing` | Nothing to say yet. Nothing in the record touches it. |
| `none` | Not a CV question. Handled outside the document. |
| `unscored` | Not checked yet. Nobody has set it against the record. |

Two counts: what the person has, and what a reader would find on the current page. The
gap between them is the value of the exercise.

**Then build the studio.** This is where it first exists.

```bash
J="$(python3 scripts/paths.py --job <job id>)"
python3 scripts/build_studio.py --cv "$(python3 scripts/paths.py --about)/<their CV>.md" \
    --scorecard "$J/scorecard.md" --asks-md "$J/asks.md" \
    --facts "$(python3 scripts/paths.py --facts)" \
    --job <job id>
```

**`--job` is required**: the job's role and employer name the file, put it in the job's
documents folder and key the studio's browser storage, so two jobs never share marks. **Never build a separate scorecard page.** The Score tab is the
scorecard. Hand the studio over and say what it is: their CV as it stands, scored, before
anything has changed.

**Done when:** the studio has been built and handed over with a populated Score tab,
everything the build said it had nowhere to put has been dealt with, and the gaps are
named plainly with no softening.

## Phase 4: Propose

Read the Phase 4 section of `references/studio.md`, and `references/proposing-changes.md`
and `references/rewriting.md` before drafting any line. Move the job to `Tailoring`.

`proposals.md`, in the person's folder, one entry per change, in the fields
`templates/proposals.md` shows: `Kind`, `Line`, `Currently`, `Suggested`, `Why`,
`Answers`, `Draws on`, `Costs`, and a blank `Decision`. **Entries run in page order**,
numbered P1 upward. **`Line:` is not optional**: it is the id the studio and
`render_cv.py` both build, such as `professional-experience/2/b3`, and a proposal without
a real one never reaches the person. `references/marking.md` has the table of ids. Run
the budget check and the duplication check before writing the file.

**Draft the key achievements too, into `achievements.md`**: six lines at career level,
each reaching across more than one employer, for the person to tick four to six. Rules:
`references/achievements.md`.

```bash
J="$(python3 scripts/paths.py --job <job id>)"
python3 scripts/build_studio.py --cv "$(python3 scripts/paths.py --about)/<their CV>.md" \
    --scorecard "$J/scorecard.md" --asks-md "$J/asks.md" \
    --facts "$(python3 scripts/paths.py --facts)" \
    --proposals "$J/proposals.md" --achievements "$J/achievements.md" \
    --job <job id>
python3 scripts/check.py --job <job id>
```

**Read what the build prints, every time.** Content it had nowhere to put is part of their
CV that is not on the page, and a proposal whose `Line:` is not on this CV is not in the
studio; fix both and build again. `check.py` exits 0 for nothing found, 1 for faults to
fix, 2 for a wrong command line, 3 for a missing folder.

**Then tell them, in the same breath, how the work gets back to you.** The studio keeps
every decision in their own browser and nowhere else:

> Nothing you do in there reaches me on its own. When you have been through it, open
> **hand to AI** on the edge of the page and paste the block into the chat. Or
> press **Save the decisions file** and give me `cv-decisions.json`. Then I apply it
> all to the CV at once.

**Done when:** every proposal carries a real `Line:`, `check.py` has been run and
everything it named dealt with, the studio has been built with `--proposals` and handed
over, and the person knows their CV is unchanged until they press a button in it.

## Phase 5: Decide

Read the Phase 5 section of `references/studio.md`.

**The deciding happens in the studio, on the page, not in this conversation.** So you
wait. Do not put the proposals to them one by one, do not ask which they accept, and do
not offer to work through them in the chat. They bring back the **hand to AI** block.

If they come back without it, ask for the block before doing anything else. **Never
guess at what they decided.** If they say the block is empty, the decisions are still in
that browser, and the studio must not be rebuilt until the block is out.

Only three things are still a conversation: a question about a fact only they have, which
follows the `answers.md` rules; something they ask you directly; and a suggestion sent
back with *Ask for another*. If they would rather go through it in the chat, do that, but
it is offered by them, never by you.

Record their decisions against the proposals; a rejected one stays marked rejected. **Silence
on a line is agreement**: never ask them to tick everything in the final check.

**Done when:** the hand-to-AI block has come back, every proposal carries a yes, a no, or
a rewording in their own words, and none of it was extracted from them in the chat.

## Phase 6: Assemble and rescore

Read the Phase 6 section of `references/assemble-and-print.md` before running anything,
and `references/assembling.md`.

**Close the proposals out first**: line ids are positional, so record every decision
against its proposal before the file changes shape. Then assemble:

```bash
J="$(python3 scripts/paths.py --job <job id>)"
python3 scripts/assemble.py "$(python3 scripts/paths.py --about)/<their CV>.md" \
    --decisions "$J/cv-decisions.json" \
    --out "$J/cv-<variant>.md"
```

It writes `cv-<variant>.md` with everything they decided and copies the rest through byte
for byte, and appends every removal and rewrite to `cv-<variant>-archive.md`. **Read what
it prints and tell them what is in it.** Leave the HTML comment on its last line alone; it
stops the same decisions being applied twice.

**Then rescore**: keep the first scorecard as `scorecard-before.md` in the job's folder, write
the new one against the assembled CV, and rebuild the studio from the assembled CV with the same
`--job <job id>` and **all the ledgers**, so they watch the score move.

```bash
J="$(python3 scripts/paths.py --job <job id>)"
python3 scripts/build_studio.py --cv "$J/cv-<variant>.md" \
    --scorecard "$J/scorecard.md" --asks-md "$J/asks.md" \
    --facts "$(python3 scripts/paths.py --facts)" \
    --proposals "$J/proposals.md" --achievements "$J/achievements.md" \
    --job <job id>
python3 scripts/check.py --job <job id>
```

The rebuilt studio says the CV changed, and that is right after an assembly.

**Design and the PDF are a separate, optional step.** Do not pick the design for them:
the studio shows every skin live. **Every render carries `--decisions` once a decisions
file exists**, and the PDF is printed by a real browser from the studio's own page. Then
read the PDF back as a screener would with `pdftotext`, and when a sidebar layout
interleaves, offer the trade rather than switching quietly. The commands, the file names,
the typeface check and the ATS read-back are all in `references/assemble-and-print.md`,
with `references/rendering.md` and `references/ats.md` behind them.

Record the rescore on the job with `jobs.py score <job id> --scorecard ... --as after`.

**Where the documents go:** the job's own folder inside `4 Finished documents`, which
`python3 scripts/paths.py --job <job id> --job-documents` names, and into the chat as well when
the session is temporary. When the final PDFs are printed, move the job to `Ready`.

**Done when:** `assemble.py` exited 0, `cv-<variant>.md` and its archive are in the
person's folder, what it printed accounts for the whole decisions file, `check.py` has
been run and dealt with, and the rescore is shown beside the first score with any ask that
did not move said out loud.

## Phase 7: The cover letter

Read `references/cover-letter.md` and the Phase 7 section of
`references/assemble-and-print.md` before writing a line.

**Written last**, because a letter written after the scoring knows which evidence this
advertisement wants. `cover-letter-<variant>.md`, in the person's folder. One page, four
to six paragraphs, doing the one job the CV cannot: why this person, for this job. The
letterhead is the CV's letterhead; the addressee and position number come out of the job
pack.

**Print it on the skin the CV is already on**, in one run, so the two cannot drift:

```bash
J="$(python3 scripts/paths.py --job <job id>)"
python3 scripts/render_cv.py "$J/cv-<variant>.md" --letter "$J/cover-letter-<variant>.md" \
    --decisions "$J/cv-decisions.json" \
    --layout sidebar-dark --palette forest --head-font lora --body-font source-sans \
    --job <job id> --pdf
```

The skin flags are whatever they landed on in Phase 6. **Leave the letter prompts in the
studio alone until they ask for a letter.** Then build the studio once more with
`--letter`, and keep rebuilding on every change to the letter.

**Done when:** it is one page, every claim in it traces to the record, and there is not
one defensive sentence in it.

---

## Fact alignment across variants

Once a person has more than one CV variant, they will drift. Run
`references/assembling.md`, section "Aligning variants", whenever a second variant exists
or an old one resurfaces. One facts ledger, many variants: tailoring changes which facts
print and how they are worded, and never what is true.

## What this skill will not do

- Write a claim the person cannot defend in an interview.
- Promote a verb. Contributed to is not led. Ask instead; the answer is usually yes.
- Invent or round a figure, including rounding a career span up to the next year.
- Rate a person's skills for them. If their CV gives levels, keep them. If two CVs
  disagree, record both and ask.
- Put a gap, an apology or a defensive sentence into a document the person sends.
- Cut something without saying so and why.
- Let a renderer decide what the CV says.
- Hand over a PDF whose typefaces the browser substituted, or one drawn as a
  picture with no text in it.

## Files

| File | Read it when |
|---|---|
| `references/voice.md` | First, always, before writing anything |
| `references/working-with-the-person.md` | Once, at the start: the rules on talking to them and never asking twice, in full |
| `references/where-files-go.md` | The first time a script runs or a file is handed over |
| `references/sources.md` | Phase 1, in full |
| `references/atomising-sources.md` | Phase 2 |
| `references/studio.md` | Phases 3, 4 and 5 in full, and the rebuild rule |
| `references/scoring.md` | Phase 3 |
| `references/proposing-changes.md` | Phase 4, before writing any proposal |
| `references/rewriting.md` | Before drafting any suggested line |
| `references/marking.md` | Before touching the studio's per-line decisions |
| `references/achievements.md` | Before drafting key achievements or adding a section |
| `references/assemble-and-print.md` | Phases 6 and 7 in full: assembly, design, PDF, letter |
| `references/assembling.md` | Phase 6, and whenever a second CV variant exists |
| `references/ats.md` | Before handing over any PDF: what the screener actually gets |
| `references/rendering.md` | Only if the person wants a designed CV or a report |
| `references/cover-letter.md` | Phase 7, before writing a line of the letter |
| `references/arithmetic.md` | Any time a number, date or year count is involved |
| `templates/` | Shapes for facts, answers, asks, proposals, scorecard, achievements, cv, job.json |
| `scripts/paths.py` | `--status` first, `--choose` once; then in every command that names a file |
| `scripts/jobs.py` | Phase 1 `list` and `new`; `stage`, `score`, `set`, `note` as the work moves; `apply-desk`, `adopt` |
| `scripts/build_desk.py` | Resu Desk. Rebuilt on its own; run it only to rebuild by hand |
| `scripts/documents.py` | What they have already produced, and for which job |
| `scripts/build_studio.py` | Phase 3, then rebuilt in 4, 6 and 7: the studio |
| `scripts/check.py` | With `--job <job id>`, at the end of Phase 4 and the end of Phase 6 |
| `scripts/assemble.py` | Phase 6: bakes the decisions into the markdown and writes the archive |
| `scripts/render_cv.py` | Markdown CV to printable HTML and PDF, 900 skins |
| `scripts/render_report.py` | Only if they ask for the score as a page of its own |
| `scripts/to_pdf.py` | The print engine. Never called directly; `--pdf` uses it |
| `scripts/fetch_fonts.py` | Once, on a machine with internet, so PDFs stop needing one |
| `assets/skins.json` | Layouts, palettes and typesets. Add one by adding a row |
