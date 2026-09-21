# Changelog

## 0.7.2, 21 September 2026

- Keep default application data in exactly `Resu - CV Builder` beneath the current
  task workspace. Ignore global folder records, install pointers and host data-folder
  variables; different destinations and imports require an explicit user instruction.
- Keep application evidence and answers in the active job folder. Do not automatically
  reuse shared history or old outputs, resume a matching job, or invent a fresh root.
- Give each application a random persistent browser identity. A recreated job cannot
  inherit old decisions even when its folder, role, employer and visible ID match.
  Rebuilds of the same application preserve its own decisions.
- Keep the hidden preview measurable while Writing or Score is open, and resize it
  when pagination finishes. All CV pages render on initial load without a skin change.
- Clarify the ordered application flow and update the documented commands to use
  application-local sources. Retain the mode-specific rewriting and full-profile rules.

## 0.7.1, 21 September 2026

- Use a guarded, single browser launch of the exact generated Studio. Always hand
  over labelled Resu Studio and Resu Desk links; rebuilds do not reopen windows.
- Require the complete, faithfully quoted original profile in writing comparisons.
  Rewrite examples and the chosen full CV in the mode's tone and positioning;
  condensed comparison examples never set the full rewrite's length.
- Preserve profile breadth, experience detail, evidenced pillars and distinctive
  contribution. Full generated profiles need at least four substantive paragraphs;
  publication checks changed profiles and requires a source-to-draft preservation review.
- Treat existing page and bullet counts as a baseline, rather than forcing additions
  to displace useful evidence. Preserve paragraph boundaries when assembling additions.

## 0.7.0, 21 September 2026

**Choose a writing direction before the full rewrite.** The Studio opens on a Writing
tab with a guiding brief and profile and experience-bullet samples based on the person's
own evidence. Compare credible conviction, direct and focused, warm and grounded, and
expressive and distinctive modes, or explore a personal direction. Every mode shares
the same requirements for factual support, ATS readability, human engagement and
tailoring to the particular advertisement.

**One choice starts the rewrite.** "Use this mode and rewrite my CV" creates a request
to send to the AI chat, including the selected mode and current review decisions. The
agent proceeds when it receives that request. The local page does not run an AI itself.
Choosing a mode authorises suggestions; each wording change still needs review.

**Personal modes and earlier work are retained.** Refine a custom option in place, or
explicitly save it for another application. Switching back to a matching saved round
restores it without generating it again. Manual edits and keep decisions survive mode
changes, and unchanged suggestions can be reused. Changed sources or evidence require
fresh review; different wording never inherits an earlier approval.

**The whole application stays connected.** Desk shows the selected mode and next writing
step. Versioned briefs, source snapshots, requests and suggestions link each decision to
the exact wording reviewed. Assembly and final review preserve approved content, section
ordering and additional sections such as projects and languages.

**Updated guidance and release examples.** Writing quality is reviewed separately from
requirement coverage. The README demonstrates the Writing view and current Studio with
fictional sample data. Testing instructions use generic local paths.

**Default PDF reading order checked.** Section headings in the timeline layout now
extract beside their content, instead of collecting before the candidate's name.
Regression tests check the full extracted text from the renderer and Studio print view,
including a multi-page document. The Windows test report also writes Unicode as UTF-8.

## 0.6.0, 17 September 2026

Resu Studio now works on more than one job at a time, shows every application on one page,
and asks where a person's private files should live before it keeps any.

**Every job ad is its own job.** A new advertisement used to replace the last one's asks,
scorecard, proposals and letter. Each ad now gets a folder of its own under `3 Jobs`, with a
`job.json` holding its role, employer, link, closing date, stage, scores and notes.
`scripts/jobs.py` starts, lists and moves jobs through nine stages, from Saved to Offer,
Rejected or Withdrawn. The CV and the facts ledger are shared by every job.

**The Studio, the PDF and `check.py` take `--job`.** Role and employer come from the job's
record, and every document lands in that job's own folder. The studio's browser storage is
keyed exactly as before, so marks already made are still there. `studio.html` itself did not
change.

**Resu Desk.** `4 Finished documents/Resu Desk.html` lists every application: stage, closing
date (flagged in the last week), the score before and after tailoring, and links to each
Studio and PDF. It rebuilds itself whenever a job, a studio or a PDF changes. A stage, a
closing date or a note changed on the page comes back through hand to AI or a saved
`desk-updates.json`, and `jobs.py apply-desk` writes it. A change made on an out of date Desk
is refused by name instead of written over the newer value.

**Where private files live is the person's choice.** Every install used to share
`~/.resu-studio`, so an install inside one project found an application started somewhere
else. Nothing is kept now until the person chooses, once per install, with
`paths.py --status` and `paths.py --choose`. Older work anywhere on the computer is listed
and brought in only when they say so, with `--bring`.

**A new folder layout, private by default.** `Resu - CV Builder` holds `1 About me`,
`2 My record`, `3 Jobs` and `4 Finished documents`, with a `README.txt` and its own
`.gitignore` of `*`, so git ignores all of it wherever it sits. Work from before jobs had
folders becomes a job with `jobs.py adopt`. Nothing is moved or deleted anywhere.

**Python is found where it actually is.** On Windows an assistant tried `python3`,
`python` and `py`, and gave up on a machine whose Python came with Miniconda or Anaconda,
which their installers leave off the PATH. `scripts/find_python.ps1` (PowerShell) and
`scripts/find_python.sh` (bash, zsh, Git Bash) look in an active conda environment, every
usual Anaconda, Miniconda, Miniforge and Mambaforge folder, the `py` launcher, python.org
installs and the PATH, run each one, keep the first real Python 3.8 or newer, and remember
it. SKILL.md runs the finder before the first script and uses the path it prints.

**Plain words in the chat, and the Studio named up front.** A test run asked "Shall I
continue by turning Alex's CV into a facts ledger and the advertisement into a requirements
ledger?", which tells a person nothing about what they will get. SKILL.md now forbids the
skill's internal words in the chat (ledger, asks, scorecard, proposals, phases, job id,
depth), gives the plain words for each, says what to tell the person at every stop, and
promises the Studio from the first message. Reading the CV and the ad now runs straight on
into scoring, so the first thing back after the depth question is the Studio.

**Resu Desk rebuilt from the Studio's own parts.** The first Desk used its own look. It now
has the Studio's rail, brand block, tabs, labels, chips, segmented control, buttons and
drawer: a card per job with Open Studio and PDF buttons, a Next step line, an Update this
application panel, at-a-glance counts, and a How it works tab explaining every action and
stage.

**Resu Desk opens documents in a new browser tab.** Open Studio, CV PDF and Cover letter PDF
open in a new tab so the Desk stays open. Shown inside an editor or app preview, where links
cannot reach the browser, the Desk says to open it by double-clicking instead, and SKILL.md
tells assistants to open the Desk and Studio in the person's web browser, never a preview.

**SKILL.md and the references** now ask where files live first, start a job per ad, pass
`--job` on every command, move stages as the work moves and hand Resu Desk over.

**Tests** in `tools/`: `test_jobs.py`, `test_jobs_build.py`, `test_desk.py`,
`test_data_folder.py`, `test_end_to_end.py`, and `test_skill_commands.py`, which runs every
command SKILL.md documents, as written. `docs/TESTING.md` says how to run them and how to
try the branch by hand.

**Releases** are packed by `tools/build_plugin.py`, which checks every manifest carries the
same version and writes `dist/resu-studio-<version>.plugin`.

## 0.5.0, 16 September 2026

Resu Studio now installs into other AI tools from this same repository, and nothing it
does assumes it is running inside Claude.

**A strict installer could not read the skill at all.** The description in SKILL.md
held `only: not`, and a colon followed by a space inside an unquoted YAML value is not
valid YAML. Claude read it anyway. The Skills CLI, and anything else that parses the
frontmatter strictly, skipped the skill with a parse error. The colon is now a comma.

**The skill says what it needs.** SKILL.md carries `license`, `compatibility` (Python 3
and a Chromium-family browser) and `metadata`, the optional fields of the Agent Skills
standard, so a tool can say so before anyone installs it.

**One version number, in SKILL.md.** The studio's version stamp read
`.claude-plugin/plugin.json` two folders above the skill. The Skills CLI, Gemini CLI and
Copilot install only the skill folder, so every studio built there said `Resu Studio ?`.
The version now lives in SKILL.md under `metadata: version:`, the stamp reads it from
there, and `tools/sync_version.py` copies it into both Claude manifests and checks the
frontmatter the way a strict installer would.

**Windows folders work on Windows.** `paths.py` refused any path with a drive letter or
a backslash, which is right in a Linux session that cannot see `D:` and wrong on a
Windows computer, where Codex, Copilot, Cursor and Gemini CLI run. The refusal now
applies only when the scripts are not running on Windows. Every script also writes its
output as UTF-8 on Windows, where an accented letter in a CV stopped the run with
`UnicodeEncodeError` when an agent read the output through a pipe.

**`PLUGIN_DATA` is honoured beside `CLAUDE_PLUGIN_DATA`**, as the host's own data folder,
under the name the Agent Plugins standard uses. A pointer file still comes first.

**Hand to Claude is now Hand to AI.** The studio's queue, its panel, the copy button and
every sentence that named Claude now name the AI, or the chat, so the page reads
correctly in whichever tool built it. The stored values behind them are unchanged, so
marks already saved in a browser and decisions files already written still load.

**Save the decisions file saves a file outside Claude.** Without Claude's downloads
capability the button only copied the JSON. Opened as its own page in an ordinary
browser, it now downloads `cv-decisions.json`.

**SKILL.md is under 500 lines**, the size the standard recommends, down from 1,080. It
now carries the short version of every rule and phase. Nothing was taken out: the full
text moved into four new references, changed only where it named Claude or pointed
at another section, `working-with-the-person.md`,
`sources.md`, `studio.md` and `assemble-and-print.md`, and each phase names the one to
read when it starts.

**Where the work happens depends on the tool.** A new `references/where-files-go.md`
covers a temporary cloud session, the person's own computer, and a chat that cannot run
code, including the Python command on Windows and the PowerShell form of the commands.

**The README says how to install it everywhere**, with the Skills CLI for Claude Code,
Codex, Copilot, Cursor and Gemini CLI, what each kind of tool needs, and what the
scripts do on your computer.

## 0.4.4, 16 September 2026

The cover letter could not be written in the studio, and on a general resume there was
no letter at all.

**The letter page was empty and inert.** With no letter file, every line of it was built
with no text in it, so there was nothing on the page with any height to it. The toolbar
inside the sheet attaches to a line you click, and there was no line to click, so every
action on the cover letter did nothing. The letter is now a scaffold of prompts: an
addressee block, a `RE:` line, a salutation, five body paragraphs and a sign-off, each a
line that can be clicked, filled in or taken off like any line on the CV.

**A prompt never reaches paper.** It shows in Working view in grey italic inside a
dashed box, and it is absent from Final view, from the PDF and from the markdown the
studio hands over. Save as PDF on a letter that is still prompts prints the resume alone
and says why. Wording the person puts on a prompt prints like any other line.

**One box for the whole letter.** Write the letter at the top of the page takes a
letter pasted or typed in full. It is read by shape rather than by markup, the same way
`parse_letter` reads the file, so a date, an address block, a `RE:` line, a `Dear ...`
line and a sign-off each land in their own place, and whatever is not in the paste stays
a prompt.

**What is written there stays written.** The letter is saved against that application
and survives a rebuild. A rebuild carrying a written letter file no longer replaces it:
a banner at the top of the page says the other letter arrived and offers it, and the
person chooses.

**The studio hands the letter back as markdown.** Copy settings and Save as PDF write
the finished letter out under the render command, to be saved as
`cover-letter-<variant>.md`. So a letter written in the browser prints on the same
layout, palette and typeset as the resume, which is what a general resume never had.

**A subject line of its own.** `cover-letter/re` is a new addressable line above the
salutation, carrying the role title as the advertisement writes it. `parse_letter` reads
`RE:` and `Subject:` on either side of the salutation, and a subject line ending in a
comma is no longer mistaken for the salutation and no longer swallows the real one.

## 0.4.3, 3 September 2026

Two instruction changes. The seven phases and everything they do are unchanged.

**The studio comes back every time the page changes.** It was built at four named points
and nothing covered a change asked for in the chat in between, so somebody could approve
work and be handed nothing to look at. A standing rule now says that any time something
that would appear on the page changes, the studio is rebuilt and the file handed back in
the same reply, without being asked for. An accepted suggestion, their own rewrite, a
line taken off, a line added, a section added, a reorder, a fresh score and a different
skin all count. Phase 5 keeps its own rule that a studio is not rebuilt while the
person's decisions are still only in their browser.

**Suggestions are ordered by where they sit on the page.** They used to be grouped by
urgency, which sent the person jumping back and forth through their own CV. They now run
top to bottom: sections in the order the CV sets them out, roles in the order they
appear, bullets in the order they appear, skills groups in the order they are drawn, and
numbered P1 upward in that same order, so the number in the chat agrees with the position
on the page. The seven kinds of change are all kept and each entry now records its own in
a Kind field, so nothing is lost about why a change is being proposed.

## 0.4.2, 3 September 2026

Fixed pages ending several centimetres short in the middle of a CV.

A role was split for pagination into a first atom carrying the heading, the intro
paragraph and the first bullet, then one atom per remaining bullet. On a role with a
real intro paragraph that first atom is large. Measured on a real CV it came to 178
pixels, and the sheet before it had 206 pixels free, which the card's own top margin
took past the line. The whole role moved to the next page and left 5.4cm of white
behind it.

The first bullet is now folded into the head only when the head would otherwise be a
bare heading, so a heading is still never stranded on its own, and a role that carries
an intro paragraph can end a sheet after its paragraph and run its bullets on.

Measured on that CV, the sheet went from 79 percent full with 206 pixels free to 93
percent full with 75 pixels free.

## 0.4.1, 3 September 2026

Fixed the extra white space at the foot of every printed page.

The paginator measures the page on screen and then the document is printed with the
print stylesheet. That stylesheet set `line-height: normal` on the sheet, which cascaded
into every paragraph and every bullet, so the text set tighter on paper than in the
layout the paginator had measured. Each page therefore ended about a tenth of a page
above where the preview showed it ending, and the effect was the same whatever paper
size was chosen.

Measured on one document before and after: the last ink on each page moved from 76, 79
and 82 percent down the page to 85, 88 and 91 percent, and the screen and print layouts
now measure identically at 883, 958, 991 and 1034 pixels rather than the print falling
back to 814, 856, 894 and 931.

The same rule was in the studio, so the preview and the studio's own Save as PDF were
both affected. Both are fixed.

## 0.4.0, 2 September 2026

A correctness pass. An audit of 0.3.0 found 25 code defects and about 30 places where
the documentation contradicted itself or the code. An end to end acceptance test then
found ten more. All of them are fixed. The record is in `docs/audit-2026-09-02.md` and
`docs/test-run-2026-09-02.md`.

### The ones that produced a wrong document

- **The bundled typefaces were never used.** All five typesets named Georgia and
  Helvetica Neue, which match nothing in the font set, so nothing was embedded and the
  substitution check found nothing to complain about. A default PDF printed in whatever
  the machine happened to have and reported success. The typesets now name Lora, Arimo,
  Source Sans 3 and Work Sans, the faces are embedded and subset, and the check can fire.
- **A CV with the dates on their own line refused to render**, which is the shape the
  parser's own notes say almost everyone writes.
- **The studio and the renderer built different line ids** for some section headings, so
  decisions made in the studio were silently dropped at print.
- **A multi paragraph profile** was one line in the studio and several in the renderer,
  so removing it still printed paragraph two.
- **Skills edits did not print** in four of the six skills treatments.
- **The paginator measured the whole document in the fallback typeface**, because a
  browser fetches a face only when it draws text in it and every word starts hidden. It
  counted lines that were not there and broke pages early. The test CV came back from
  two pages to one.
- **Pages could be dropped or duplicated.** A skills group could vanish on a layout with
  no sidebar, two groups sharing a heading collided on one id, and a plain line under a
  labelled skills line was swallowed into the skill above it.

### Where the person's files live

- The default folder moved out of the plugin to `~/.resu-studio`, so a plugin update
  cannot delete somebody's history. Anything left in the old folder is copied out on the
  first run, never moved and never written over.
- The pointer file has a stable home outside the plugin as well, so an update cannot lose
  the pointer either. A pointer now beats the `CLAUDE_PLUGIN_DATA` environment variable.
- A Windows path or a relative path in the pointer is refused with a plain message
  instead of quietly creating a folder whose name contains the backslashes.
- `paths.py` can print one bare path for a command line, so a ledger is never written to
  a working directory that is thrown away at the end of the session.
- The employer is part of a document's identity, so two applications for the same job
  title at different employers cannot overwrite each other.

### Phase 6 assembles for real

- New `scripts/assemble.py` writes the tailored CV. It applies every rewrite, takes out
  every removal, puts in every added line, follows the order the person chose, and writes
  in every section they ticked. The result is a complete document that renders correctly
  on its own.
- `cv-<variant>-archive.md` holds every line taken off, in full, with the reason and the
  date, and both wordings of every rewrite.
- The assembled file records which decisions are already in it, so nothing is ever applied
  twice.
- A studio rebuilt on a changed CV now says on the page what carried over, what it put
  back by matching wording, and what it dropped, and keeps the previous state so it can be
  recovered.

### The studio

- `--role` is required, and the employer is in the filename and the storage key.
- Both ways of handing work back now carry the same decisions. A rejection and a question
  survive in the decisions file, and ticked achievements survive in the pasted block.
- A proposal whose right answer is a question now reaches the person instead of being
  dropped.
- The page makes no network requests at all.
- Content the studio cannot hold, and a proposal naming a line that is not on the CV, are
  both reported rather than passing silently.

### Refusals instead of guesses

- A missing paginator refuses instead of printing a blank page.
- A malformed decisions file refuses in one plain sentence instead of a stack trace.
- A page less than a quarter full is reported so nobody ships a nearly empty last sheet
  without knowing.

### Documentation

Every example identity was taken out of the shipped files. The reference files and the
templates used to carry a named employer, a named job title and a named person, some of
it apparently lifted from a real CV when the skill was first written. They now carry
placeholders in the skill's own bracket style, which also brings the files into line with
the skill's own rule against illustrating anything with an invented occupation.

Every command block published in the skill has now been run. The extraction behaviour of
all eighteen layouts was measured rather than repeated: all eight sidebar layouts
interleave once extracted, including the default, so the guidance offers the trade
instead of claiming there is nothing to trade.

## 0.3.0

The version this work started from.
