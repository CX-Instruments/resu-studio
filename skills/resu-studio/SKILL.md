---
name: resu-studio
description: This skill should be used whenever the user is applying for a job, or preparing anything an employer will read. Trigger on "I want to apply for a job", "help me with my CV", "look at my resume", "tailor my CV to this ad", "write me a cover letter", "am I a good fit", "should I apply for this", "why am I not hearing back", "get past the ATS", and on any mention of a CV, resume, curriculum vitae, cover letter, covering letter, motivation letter, supporting statement, personal statement, statement of claims, selection criteria, job ad, vacancy, job posting, position description or duty statement, or on updating, rewriting, rewording, proofreading, shortening or restructuring any of them. It scores the person against the advertisement before changing anything, proposes every change for them to accept or reject one at a time, and prints a PDF a screening system can still read. Applicant side only: not for writing job advertisements or screening candidates.
---

# Resu Studio

Seven phases, in order. Each writes files and stops. The person decides between phases.

```
1. SOURCES     capture the ad and every CV variant, verbatim, unedited
2. ATOMISE     facts ledger from the CVs, asks ledger from the ad
3. SCORE       you against it, before any changes
4. PROPOSE     every change as current / suggested / why, inside a bullet budget
5. DECIDE      the person accepts, rejects or asks for a rewrite, item by item
6. ASSEMBLE    the CV as markdown, then rescore
7. LETTER      one page, written last, because it needs the score to exist
```

**Read `references/voice.md` before writing a single sentence for this person.** It
governs everything: the CV, the statement, the letter, and how you talk to them in
chat. It is short.

---

## Say what this is, once, before asking for anything

**Somebody who typed "can you help with my CV" does not know a tool engaged.** They do
not know it runs in steps, that it stops for them at every one, or that it will score
before it changes a word. If you go straight to asking for files, they cannot tell you
apart from any other answer, and they will not know what they are being offered.

So open with two or three plain sentences: that you work through the advertisement and
their CV in order, that you score where they stand before changing anything, and that
they accept or reject every change themselves. Then ask for what you need.

**Once per conversation, and never as a menu.** Do not list the seven phases at them
unless they ask what it does. Do not make them read a tool log to find out what they
are talking to.

## End every phase by saying what happens next

**Each phase stops and waits for them. That is the design, and it is invisible.** From
where they sit the work simply stopped, with no way to tell whether you are finished,
stuck, or waiting. A person who does not know it is their turn will sit there, or
worse, close the tab believing that was the answer.

So close every phase with three things, in two or three plain sentences:

- **what just came out of it**, in one line
- **what you need from them**, if anything, and why it changes the outcome
- **what the next phase does**, so they know what they are agreeing to before they
  agree to it

Then stop. **Their answer starts the next phase. Finishing one is not permission to
begin the next**, and this matters most after scoring, which is the longest step and
the one they paid for: somebody who has just been handed a hard number deserves to be
asked before anything of theirs gets rewritten.

Never present this as a menu of seven phases. One or two sentences, in their language,
about the thing in front of them.

## Assume nothing about their work until their CV arrives

**You do not know what they do.** Not the trade, not the seniority, not the country,
not whether the employer is a hospital, a building firm, a school, a farm or a bank.
So: do not reach for an example from any occupation, do not guess what their skills
section might hold, do not assume an advertisement has criteria or a pack or a word
limit, and never describe this skill as being for a kind of role. Every rule in
`references/` is about writing and evidence, and holds whoever they are.

**The moment their CV is in, be specific.** Use their words, their employers, their
tools, their level words, their spelling. Draw every illustration from their own
lines: a rule shown on their bullet persuades, and the same rule shown on a
stranger's tells them this was built for somebody else.

## Where the work happens, and where the files go

**Run every script in your own session, not on the person's computer.** The scripts
need a Chromium-family browser to print the PDF, and the session has one. A person's
machine usually does not, and a non-technical person should never be asked to install
anything, set a path, or type a command. They should not have to know that any of this
is Python.

**Then hand the finished files over. Every time.** The session is temporary. A CV
written there and not delivered is gone when the session ends, and the person will not
know that happened until they go looking. So:

- deliver each finished document into the conversation, as a file they can open, and
- write it into a folder on their own computer when one is connected, and say which
  folder and what it is called, in plain words.

**Their folder is `~/.resu-studio`, unless somebody named another one.** That is
outside the plugin, so a plugin update cannot delete it, and it is where `facts.md`,
`answers.md`, `cv-source/` and `_Your Documents Are Here/` all live. Run
`python3 scripts/paths.py` to see the folder and why it was chosen. Nothing about this
needs setting up: the default already survives an update.

**If they have a folder connected, point at it, so their record sits on their own
disk.** One line, the folder, in either pointer file:

- `~/.resu-studio/location` is the stable one, outside the plugin.
- `data-location.txt` beside `SKILL.md` still works and is copied out to the stable
  one the first time it is used, so the next update cannot lose the pointer.

A pointer beats the `CLAUDE_PLUGIN_DATA` environment variable, because a person
writing a path has said what they want and a host guessing one has not.

**Write the path as this session sees it.** A Windows path like `D:\Users\Jane\CVs`,
or any path with a backslash in it, or a relative path, is refused with a plain
message rather than quietly building a folder whose name contains the backslashes.
A person on Windows has their folders mounted somewhere under a session path that
starts with `/` and has no drive letter, usually something like
`/home/<you>/mnt/<folder>`. `paths.py` looks for a mounted folder with the same name
and says which one it found, so read the message rather than guessing at a path.

**`--pdf-dir` moves rendered output and nothing else.** It does not relocate
`facts.md`, `answers.md` or the CV as it arrived. Those follow the pointer.

**Anything left in the old in-plugin folder is copied out on the first run.** The old
folder is left exactly as it was. Nothing already in the new folder is written over,
and the run says on screen what it did and what it left alone. It happens once. If the
person sees that message, it is their own history being brought somewhere an update
cannot reach.

**Never send them a command to run.** The studio prints one for the design they land
on, and that is for you to execute, not for them.

**Every command that names a ledger uses `paths.py` to name it.** A bare relative
`facts.md` resolves against the session's working directory, which is thrown away at
the end of the session, so the file the next advertisement needs is gone. Write it as
command substitution, every time:

```bash
python3 scripts/paths.py --facts       # one bare path, nothing else
python3 scripts/paths.py --data        # the folder the ledgers live in
python3 scripts/paths.py --answers
python3 scripts/paths.py --cv-source
python3 scripts/paths.py --documents
```

Every command block below is written that way, and so is every command you write that
is not in this file.

## Never ask the same question twice

Asking a person something they already told you is the fastest way to lose their
trust in the whole exercise, and it happens because the answer was used and then
dropped. Every answer gets written down, in a file, the moment it arrives.

**The file is `answers.md`, in the same folder as `facts.md`**, the resolved data
folder that `python3 scripts/paths.py --answers` names, so it survives this session
and every later job ad. Create it on the first question. Its shape is
`templates/answers.md`.

One block per question, appended in the order asked:

```
q: The question, in the words you actually put to them
a: What they said, verbatim where you can
on: 2026-09-01
phase: 4
led to: fact-team-size          # or: nothing
```

The rules, and none of them are optional:

- **Read `answers.md` before you ask anything.** Before every question, in every
  phase. If the question is already in the file, you have your answer. Use it and
  move on.
- **Write the answer before you use it.** Not at the end of the phase, not when the
  file is next touched. The moment they answer.
- **A "no" is an answer.** "I don't have that", "I'm not sure", "I'd rather not say"
  and "it was AI-written" all get written down exactly like a yes, and none of them
  are ever asked again. Unanswered questions are the only ones that come back, and
  they come back once, named as unanswered.
- **An answer that is a fact about them goes to `facts.md` as well**, as a `stated:`
  source. `answers.md` records that you asked; `facts.md` records what is true. Put
  the fact id in `led to:` so the two files point at each other.
- **Do not re-ask a question in different words.** Check what the file already
  covers, not whether the sentence matches.

If they change their answer later, add a second block rather than editing the first,
and use the newer one. What they said and when is part of the record.

## The three rules that matter most

**1. A fact is not a printed line.** The facts ledger holds everything the person has
ever written about their working life. The page holds a small selection of it. These
are different things and conflating them is what produces a six page CV. Every
printed line traces to a fact; most facts do not print.

**2. Every slot has a budget, declared before anything is written.** A role has a
bullet count. The skills column has a line count. The page has a page count. An
addition requires a removal, or an explicit decision by the person to raise the
budget. Nothing is ever cut silently: a removal is a proposal like any other, with
its own reason, and the person can refuse it.

**3. A claim prints once.** Before proposing any line, check every other slot on the
page for the same claim. Role bullets and achievement panels repeat each other by
default, and a reader who notices reads the second copy as padding. See
`references/proposing-changes.md` for how to split a partial overlap so each half
keeps what is unique to it.

---


## Phase 1: Sources

### First: is there already an application in progress?

Before copying anything in, run `python3 scripts/documents.py`. It lists what this
person has produced and which advertisement each file was for.

**If it lists an advertisement other than this one, stop and say so before doing any
work.** Name what survives as well as what does not. A warning that only lists losses
reads as "you are about to lose everything", and people click through those. Something
like:

> Starting **<the new advertisement>** will change what is in the studio.
>
> **Kept:** your CV, your history in `facts.md`, and every PDF you have already
> produced, including the earlier ones.
> **Replaced:** the asks ledger, the scorecard, and the draft CV and letter for
> the advertisement you were working on.
>
> Nothing already finished is deleted. Shall I start the new one?

Then wait. Do not begin Phase 2 until they answer.

**Two things make this safe rather than merely announced.** `facts.md` lives in the
person's own folder and is never rewritten by a new advertisement, so read it and do
not rebuild it. And every render passes `--role "<the job title>"` and
`--employer "<the employer>"`, so each application writes its own PDF instead of two
applications sharing one filename. When a file would be written over by a different
application anyway, the earlier one is kept under a dated name and the render says so.
Re-rendering the same application on another skin replaces its own file, which is what
somebody trying six skins wants.

**Never pass `--role` or `--employer` for one advertisement while working on
another.** That is the one thing that would let a document be written over: those two
names are what tell two applications apart.

Copy every source into `cv-source/` untouched, which is the folder
`python3 scripts/paths.py --cv-source` names: the advertisement, the job pack if there
is one, and every CV variant. Extract the text of each into a `.txt` beside it, so a
later session can re-read without the original.

**Then write the CV out as markdown in the `templates/cv.md` shape, into
`cv-source/`.** Nothing later in this skill can read a PDF or a Word file. Phase 3
builds the studio from a markdown CV, and `build_studio.py` refuses markdown with no
`# Name` heading, so a CV that arrived as anything else has to be converted here or
Phase 3 has nothing to open. Convert it faithfully: their headings, their wording,
their order, their spelling. The file format changes and the content does not, so no
line is reworded, dropped or tidied on the way through.

Ask for what is missing. Advertisements of every kind point at a second document
and assume you will go and read it: a job pack, an applicant kit, a position
description, a candidate information pack, a duty statement, a person specification.
Whatever it is called, that is usually where the real criteria, the application
format, the page limit and the eligibility conditions are. **Whenever an
advertisement references one, ask for it.** Working from the advertisement alone
produces a confident answer to the wrong question. If a URL will not fetch, say so
and ask for the text rather than reconstructing the ad from its title.

**Done when:** every source is on disk in the person's own words, the CV is saved in
`cv-source/` as markdown in the `templates/cv.md` shape with a `# Name` heading at the
top of it, and the application format is known: what documents, what word limits, what
page limit.

### Then stop and ask how deep to go. Before you read anything else.

Scoring a history against an advertisement is by far the longest job in this skill, and
how long depends entirely on how much of the advertisement gets scored. **That is the
person's decision and it costs them, so they make it before the work starts, not after
they have paid for it.**

**Some advertisements label this split and many do not.** Essential and desirable,
required and preferred, must and nice to have, or nothing at all and you work it out
from how the thing is written. Ask about the split by what it means, never by a label
the advertisement did not use.

Ask it plainly, in these terms, and wait for an answer:

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

**Record the answer in `answers.md`, the moment it arrives**, like every other answer,
as `depth: essentials` or `depth: all`. The scorecard does not exist yet. When it is
written in Phase 3, copy the same word into its frontmatter as `depth:`, which is
where `build_studio.py` reads it and where every later session finds it without asking
again.

**Never choose for them, and never quietly do the bigger job.** If they have not
answered, ask again rather than assuming. Doing the full pass uninvited spends someone
else's limit on a decision they did not make.

## Phase 2: Atomise

Two ledgers. `facts.md` and `asks.md`. Templates in `templates/`.

**They do not live in the skill.** Run `python3 scripts/paths.py` to see where this
person's folder is; that is where `facts.md`, `asks.md`, `answers.md`, `cv-source/`
and their finished documents go. Write them there and name them there:
`"$(python3 scripts/paths.py --data)/asks.md"`, and
`"$(python3 scripts/paths.py --facts)"` for the facts ledger. A file written to a bare
relative name lands in the session's working directory, which is thrown away when the
session ends, and the next advertisement then finds no history and rebuilds one that
already existed.

The facts ledger is the reusable asset. Build it once per person and add to it. It
survives every application and every CV variant.

**On a second advertisement, read it. Do not rebuild it.** If `facts.md` is already
there, the person's history is already known: the new advertisement needs a new asks
ledger and nothing else. Ask them for their CV again only when there is no facts
ledger, or when they say something has changed.

The asks ledger is per advertisement. Split compound asks: a duty naming seven
subjects in one sentence is seven asks, not one, or the person will read as failing
all of it when they answer five.

Full instructions: `references/atomising-sources.md`.

**Done when:** every printable line of every CV variant is a fact with an id, every
ask has an id and a necessity, and any place two CV variants state the same fact
differently is recorded as a conflict rather than resolved.

## Phase 3: Score, before changing anything

**Score to the depth they chose in Phase 1.** On `essentials`, score every ask marked
`must` and mark the rest `unscored`. Unscored is not missing: missing means you looked
and found nothing, unscored means nobody looked. Never let one read as the other, and
never count an unscored ask toward what the person has.

Say how many are unscored every time you report a score, in the same sentence as the
number. A score of sixteen of eighteen essentials with eleven asks untouched is an
honest answer; the same number with the untouched ones unmentioned is not.

`scorecard.md`, in the person's folder. Copy the depth they chose in Phase 1 into its
frontmatter as `depth: essentials` or `depth: all`; that is where `build_studio.py`
reads it. Necessity on every row is one of five words: `must`, `nice`, `implied`,
`condition`, `not a cv question`. The studio draws all five with labels of their own,
so a citizenship or licence condition is shown as a condition of the job rather than
as a soft item lifted off the role description.

Every ask gets one of these states, and these are the words the studio and the printed
report both use, so all three describe an ask the same way:

| state | means |
|---|---|
| `page` | On your CV. A line answers it, in wording close to theirs. |
| `buried` | On your CV, your wording. The work is there; their term for it is not. |
| `off` | Left off this CV. The record answers it and this variant does not carry it. |
| `near` | Half answered. Part is answered and nothing claims the rest. |
| `missing` | Nothing to say yet. Nothing in the record touches it. |
| `none` | Not a CV question. Handled outside the document. |
| `unscored` | Not checked yet. Nobody has set it against the record. |

Two counts, not one: what the person has, and what a reader would find on the current
page. The gap between those two numbers is the entire value of the exercise.

**Then build the studio, at the end of Phase 3.** This is where it first exists. It is
rebuilt in Phase 4 with the proposals in it, and again in Phase 6 from the assembled
CV. A rebuild for the same role, employer and CV file replaces this same page. The
Phase 6 rebuild reads a different CV file, so it keeps this one under a dated name and
says where it went, which is what you want: the score before and the score after are
both still on disk.

A table of rows is not a score anybody can take in, and this is the first moment the
person has something real to look at: their own CV, drawn, with the score beside it.
Everything up to here has been the skill's working papers.

```bash
D="$(python3 scripts/paths.py --data)"
python3 scripts/build_studio.py --cv "$(python3 scripts/paths.py --cv-source)/<their CV>.md" \
    --scorecard "$D/scorecard.md" --asks-md "$D/asks.md" \
    --facts "$(python3 scripts/paths.py --facts)" \
    --role "<the job title>" --employer "<the employer>"
```

The `--cv` is the markdown written in Phase 1: their CV as it arrived, converted into
the `templates/cv.md` shape and changed in no other way.

**`--role` is required and the build refuses without it.** It names the file, and it
is half of the key the studio's browser storage uses. `--employer` is the other half,
so two employers hiring the same job title do not share one set of marks.

The Score tab is the scorecard. It reads the three files you have just written: the
advertisement's own wording from `asks.md`, the state of each ask from `scorecard.md`,
and the verbatim line that answers it from `facts.md`. It draws the two counts, every
ask worst first, and the line on their CV that answers it. **Never build a separate
scorecard page.** There is one place a person reads their score, and it is the studio.

The studio carries its typefaces inside itself rather than fetching them from a font
server, so the preview measures its page breaks in the same metrics the print uses.

Hand it over and say what it is: their CV as it stands, scored, before anything has
been changed. The markdown files are the record behind it and are handed over too,
but the studio is the thing you point them at.

Full instructions: `references/scoring.md`.

**Done when:** the studio has been built and handed over with a populated Score tab,
everything the build said it had nowhere to put has been read and dealt with, the
person can see where they stand before a single word has changed, and the gaps are
named plainly with no softening.

## Phase 4: Propose

`proposals.md`, in the person's folder. One entry per change. The `## P1.` heading
carries the location in words. Every entry then carries these fields, which are the
ones `templates/proposals.md` shows and `build_studio.py` reads:

```
Line          the studio's id for the line this lands on
Currently     the full existing text, verbatim, or `Not on the CV.`
Suggested     the full replacement text, ready to paste, or `Delete this bullet.`
Why           one or two sentences
Answers       which ask ids this serves
Draws on      which fact ids this rests on
Costs         on an addition, which line comes out or how the budget rises
Decision      left blank, for the person
```

**`Line:` is not optional.** It is the id `render_cv.py` and the studio both build
from the markdown, such as `professional-experience/2/b3`, `profile/0` or
`key-skills/technical`, and it is what puts the suggestion on the right line of the
page. A proposal without one cannot be shown against anything and does not reach the
person. A proposal whose `Line:` names an id that is not on this CV is left out for
the same reason, and the build names it. `references/marking.md` has the full table of
ids.

Additions say `Currently: not on the CV`, and their `Line:` is the line they print
after. Removals say `Suggested: delete this bullet` and always carry a reason.

Run the budget check and the duplication check before writing the file, not after.

**Then rebuild the studio with the proposals in it.** Same command as Phase 3 with
`--proposals` added, same `--role` and same `--employer`, so it replaces the studio
they already have rather than making a second one. Their marks live in the browser
keyed to that role and employer, so nothing they have already decided is lost.

**Draft the key achievements too, into `achievements.md`.** Draft six lines at career
level, each reaching across more than one employer, from `templates/achievements.md`.
The person then ticks four to six of them. If a sixth line only exists to reach six, it
comes off. They are not proposals, because a proposal sits on a line that exists and
this section may not be on their CV at all, so they go in their own file and the studio
offers them as picks. Nothing prints until the person ticks it. Full rules:
`references/achievements.md`.

```bash
D="$(python3 scripts/paths.py --data)"
python3 scripts/build_studio.py --cv "$(python3 scripts/paths.py --cv-source)/<their CV>.md" \
    --scorecard "$D/scorecard.md" --asks-md "$D/asks.md" \
    --facts "$(python3 scripts/paths.py --facts)" \
    --proposals "$D/proposals.md" --achievements "$D/achievements.md" \
    --role "<the job title>" --employer "<the employer>"
```

Same `--cv` as Phase 3, because nothing has been assembled yet and every proposal sits
on a line of the CV as it arrived.

**Read what the build prints, every time. There are two things in it.**

The first is content it had nowhere to put. That is a whole section it does not know,
and now also a block inside a section it does know: a profile written as bullets, an
intro paragraph above the roles, a skills line it could not read as a group. Any of
those is a part of their CV that is not on the page, and saying otherwise is the worst
thing this skill can do. The studio holds six sections: profile, key skills,
experience, education, training and key achievements. Anything else has to be folded
into one of those or it does not print, and the person is told which and why.

The second is any proposal whose `Line:` names an id that is not on this CV. Those are
not in the studio and the person will never see them, so fix the id against the CV the
studio was built from and build again.

Then run the check.

```bash
python3 scripts/check.py
```

It reads the person's own folder, so it needs nothing typed after it. Exit 0 means
nothing found, 1 means faults to fix, 2 means the command line was wrong, and 3 means
the folder is not there.

Tell them it is the same studio, now with the suggestions in it. Each one sits on the
line it would change, showing the line they have and the line proposed, with five
buttons: **Use this**, **Edit it first**, **Keep mine**, **Ask for another**, and
**Take the line off instead**. Nothing is applied.

**And tell them, in the same breath, how the work gets back to you.** The studio keeps
every decision in their own browser and nowhere else. You cannot see any of it. Say
so, plainly, before they start:

> Nothing you do in there reaches me on its own. When you have been through it, open
> **hand to Claude** on the edge of the page and paste the block into the chat. Or
> press **Save the decisions file** and give me `cv-decisions.json`. Then I apply it
> all to the CV at once.

A person who does not know this can work for an hour and believe it was saved,
because it *was* saved, in their browser, where nothing else can read it. Leaving
that unsaid is the single most expensive omission in this whole skill.

Full instructions: `references/proposing-changes.md`.

**Done when:** every proposal carries a `Line:` that names a line the CV actually has,
`python3 scripts/check.py` has been run and everything it named has been fixed or
answered, the studio has been built with `--proposals` and handed over, and the person
has been told that their CV is unchanged until they press a button in it.

## Phase 5: Decide

**The deciding happens in the studio, on the page, not in this conversation.** Twenty
numbered items in a markdown file is not a decision anybody can make: they cannot see
what the line looks like where it lands, and being asked to approve a list they have
not seen is the thing this whole studio exists to prevent.

So in this phase you wait. Do not put the proposals to them one by one. Do not ask
which ones they accept. Do not offer to work through them in the chat. They open the
studio, press through the suggestions, and bring back the **hand to Claude** block from
its panel, which names what they used, what they kept, what they want written again,
and anything they flagged.

**Waiting is not the same as going quiet.** Say what you are waiting for and how it
gets to you, in one sentence, every time you hand the studio over. If they come back
without the block, with a question, or a screenshot, or "I have done it", ask for
the block before doing anything else. **Never guess at what they decided, and never
ask them to tell you decision by decision in the chat.** That is the copying-out job
the block exists to spare them.

If they say the block is empty or the tab shows nothing, the decisions are still in
that browser: same page, same device, and the studio must not be rebuilt until the
block is out, because a rebuild they open on a different machine will not have them.

Three things, and only these three, are still a conversation:

- a question about a fact only they have, which follows the `answers.md` rules above
- something they ask you directly
- a suggestion they sent back with *Ask for another*

If they say they would rather go through it in the chat, do that. Their preference
beats this rule. But it is offered by them, never by you.

Record their decisions against the proposals when the block comes back. A rejected
proposal stays in the file marked rejected, so a later session does not raise it again.

**When they answer a question, write it into `answers.md` before you use it, and
never ask it twice.** See *Never ask the same question twice* above for the file and
its rules. A decision on a proposal is recorded against the proposal; an answer about
their working life is recorded in `answers.md`, and the fact it produces in
`facts.md`.
When they correct you, say so plainly, fix it, and do not re-argue. Once is
information. Twice is a tool trying to win.

**Silence on a line is agreement.** The studio's final check lists the page as it then
reads, and ticking a line there is the person keeping their own place on a long page.
It is not a queue you are waiting on and it is not consent you need. **Never ask them
to go through and tick everything, never treat unticked lines as outstanding, and
never hold the CV back because the final check is not complete.** Only the suggestions
need an answer.

**Done when:** the hand-to-Claude block has come back from the studio, every proposal
carries a yes, a no, or a rewording in their own words, and none of those decisions
was extracted from them in the chat.

## Phase 6: Assemble and rescore

Write `cv-<variant>.md`, into the person's folder, from the accepted proposals plus the
untouched lines. The markdown file is the deliverable and the master.

Then rescore: keep the first `scorecard.md` as `scorecard-before.md`, write the new
one against the assembled CV, and rebuild the studio from it with the assembled CV as
`--cv`. Same `--role` and same `--employer`, so it is written under the same filename
and their marks, which are keyed to that role and employer, are all still there. The
Score tab they have been reading all along now shows the new numbers, and they watch
it move rather than being told it moved.

**Pass the ledgers on this rebuild too.** A rebuild given only `--cv`, `--role` and
`--employer` opens with an empty Score tab, no suggestions and no achievements panel,
and prints `asks : 0 (not scored yet)` while you are telling them to watch the score
move.

```bash
D="$(python3 scripts/paths.py --data)"
python3 scripts/build_studio.py --cv "$D/cv-<variant>.md" \
    --scorecard "$D/scorecard.md" --asks-md "$D/asks.md" \
    --facts "$(python3 scripts/paths.py --facts)" \
    --proposals "$D/proposals.md" --achievements "$D/achievements.md" \
    --role "<the job title>" --employer "<the employer>" \
    --letter "$D/cover-letter-<variant>.md"
```

Drop `--letter` on the first pass through Phase 6. It goes in when a letter already
exists from an earlier run, and otherwise the letter arrives in Phase 7 and this is
built again then.

Then run the check.

```bash
python3 scripts/check.py
```

Full instructions: `references/assembling.md`.

**Done when:** the markdown carries every accepted change and no unaccepted one,
`python3 scripts/check.py` has been run and everything it named has been fixed or
answered, the rescore is shown beside the first score so the movement is visible, and
any ask that did not move is said out loud rather than left for them to notice.

**Design is a separate, optional step, and it renders the markdown.** It never reads
the ledgers, never invents a line, and never truncates. It dresses both documents: the
resume and the letter always wear the same skin.

**Do not pick the design for them.** They already have the studio from Phase 4, and the
rebuild above is the page they are dressing. Let them choose. It draws their own CV
live with every layout, palette, typeface, skills treatment, section order and column
placement as a control, works on a phone, marks where A4 actually cuts, and prints the
command line for whatever they land on.

It writes into their documents folder, beside their finished PDFs. **Always pass
`--role` and `--employer`.** `--role` is required and the build refuses without it.
Together they name the file, key the studio's own browser storage so one application
cannot show another's marks, and tell two applications apart when a document would
otherwise be written over.

**The studio is built, never edited.** Editing the template by hand is what made a
second advertisement destroy the first, because there was only ever one copy. Building
the studio again for the same role, employer and CV file replaces that application's
own page. Anything else, including this rebuild, which reads the assembled CV rather
than the one from Phase 3, keeps the earlier page under a dated name and says where it
went.

Then render that.

```bash
D="$(python3 scripts/paths.py --data)"
python3 scripts/render_cv.py "$D/cv-<variant>.md" --gallery
python3 scripts/render_cv.py "$D/cv-<variant>.md" --layout sidebar-dark --palette forest \
    --skills list --skills-by "Technical=bars;Tools=chips" \
    --skills-order "Tools;Technical" --skills-place "Tools=main" \
    --gap normal \
    --order profile,key-skills:side,professional-experience,education,training-and-certifications
```

The names in `--order`, `--skills-by`, `--skills-order`, `--skills-place` and
`--hide-groups` are this person's own headings, so read them off their markdown rather
than copying the ones above. A section `--order` does not name still prints, last, in
the main column, and the render says which. Any heading with the word "skill" in it is
the skills section, whatever else it is called.

The gallery draws one page per layout and palette, 180 of them, at the typeset it was
given. There are 900 skins in all: 18 layouts, 10 palettes and 5 typesets. The five
typesets are set in bundled families rather than in whatever the machine happens to
have: Lora throughout, Arimo throughout, Lora headings over Source Sans 3, Source Sans
3 headings over Lora, and Work Sans throughout at a slightly smaller size.

**The PDF is printed, not redrawn.** `--pdf` puts the finished HTML through a real
browser and writes both documents, one file each, on whatever skin was chosen. Same
CSS, same palette variables, same paginate.js deciding the page breaks, so the file
is the studio's own page: the colours, the layout, the meters and rings, the
typefaces. The text stays text, which is what an applicant tracking system reads.

```bash
D="$(python3 scripts/paths.py --data)"
python3 scripts/render_cv.py "$D/cv-<variant>.md" --letter "$D/cover-letter-<variant>.md" \
    --layout sidebar-dark --palette forest --head-font lora --body-font source-sans \
    --role "<the job title>" --employer "<the employer>" --pdf
```

**The filename is what stops one application writing over another.** With `--role` and
`--employer` the PDFs are written as
`<Name> - <Role> - <Employer> - <YYYYMMDD> - CV.pdf` and
`<Name> - <Role> - <Employer> - <YYYYMMDD> - Cover Letter.pdf`, in that order, and a
segment with nothing in it is left out rather than printed as a gap between two
hyphens. Without `--employer`, two applications for the same job title built on the
same day produce one filename. `--date` writes the stamp however you pass it and
defaults to today as YYYYMMDD. `--out` names the HTML file, and `--pdf-dir` names the
folder the PDFs go to.

**Then read the PDF back as a screener would.** Most applications are parsed by
software before a person sees them, and what it receives is not the page you designed.
Extract the text and check three things: the name is first and whole, every section
heading appears as a word rather than spaced-out letters, and nothing is interleaved.

```bash
pdftotext "<the finished>.pdf" - | head -40
```

A two-column sidebar reads out of order once extracted. On the four right-hand sidebar
layouts, `sidebar-right`, `sidebar-tint-right`, `sidebar-line-right` and
`sidebar-top-right`, the file opens with the profile and the name arrives after the
whole main column. The four left-hand ones open with the name, wrapped onto two lines
by the narrow column. This was measured, so `references/ats.md` carries the table. That
is fine for an application going to a person and a poor bet for one going through a
job board or a government portal. Offer the trade rather than switching quietly.

Full instructions: `references/ats.md`.

**It refuses rather than guessing.** A browser that cannot reach a typeface does not
fail: it substitutes a face with different metrics, re-flows every line against it,
and writes a document that looks finished and is not the one that was approved. So
`--pdf` reads the faces back out of the finished file, and when one is missing it
deletes the PDF and says which. `python3 scripts/fetch_fonts.py` puts the font files
in `assets/fonts/` once, the renderer carries them inside the document from then on,
and the question never comes up again on any machine, with or without a network.
`--pdf-allow-substitute` overrides it, and should be rare.

**When the person pastes a command from the studio, read what came with it.**
Save as PDF hands over the command and, underneath it, the decisions as JSON: the
lines they took off this version, the ones they rewrote in their own words, the ones
they added, and any section that is not in the markdown. Write that JSON to
`cv-decisions.json` beside the CV markdown before running the command, which already
carries `--decisions`.

Skip it and the render is wrong in the worst way: it prints from the markdown alone,
so every line they deleted comes back and every rewrite reverts, and the PDF looks
finished. They will not check a document they asked you to produce. **Final** is the
right-hand half of the Working and Final switch beside the zoom, and what it shows is
what they approved. The PDF has to match it.

The decisions file also carries an `order` key, so a bullet the person moved with the
arrows in the studio prints where they put it. The render lists every list it
reordered, with the original line numbers in their new order, and every line still
prints: one the order did not name keeps its own place at the end. A decisions file
that is not valid JSON, or whose order names a line twice or names one that is not
there, refuses in plain words and writes nothing, rather than printing a document
nobody can tell is wrong.

**Where they go.** `_Your Documents Are Here/` inside the person's own folder, which
is `python3 scripts/paths.py --documents`, or wherever `--pdf-dir` says. Put them in
the chat as well: a file they cannot find is a file they do not have.

A section that is a flat list of short lines can run in two columns, in the studio or
with `--columns`. Each skills group can be drawn its own way, and one treatment applied
to all of them looks lazy. Each group also has an order, a column and a show or hide of its own: groups
can be reordered against each other, sent individually to the sidebar or the main
column so the skills section spans both, and left off a version without touching the
markdown. Hiding says which groups it took off and how many skills went with them,
because nothing here disappears quietly. A bar, a dot or a ring appears only where the markdown states a level;
everything else prints as text, so no number reaches the page that its owner did not
write. `--order` moves sections and sends them to the sidebar, and never drops one.

**A CV can grow a section.** The studio holds six: profile, key skills, experience,
education, training and key achievements. Three of those can be added to a CV that
does not have them, and they are key achievements, professional memberships, and
volunteering and community. An added section never touches the markdown: it prints on
that version, is reported as an addition, and comes off again. Key achievements is the
one you draft: six candidate lines out of their record worked against this
advertisement, each naming the ask it answers and the roles it rests on, and they tick
four to six of them. **Write them at career level.** Each line reaches across more than
one employer, so it says
something no role bullet says and nothing has to come off the page for it. A line that
restates a single bullet gets rewritten wider; the bullet is never deleted, because
that would leave the achievement with no job behind it.
`references/achievements.md`.

**Every line on the page can be pointed at.** Flag it, ask for a rewrite, put it in
their own words, take it off this version, or add one after it. Two queues on the edge
of the page keep score: what they have not decided about yet, and what they have handed
to you. Nothing touches the markdown, and everything taken off is kept in full in the
archive. `references/marking.md`.

`render_cv.py` counts content lines in and lines accounted for, and refuses to write
the file if they differ. The rescore goes into the studio the same way the first score
did: rewrite `scorecard.md` and rebuild, so the Score tab moves and they watch it
move. Contract, skins, the skills treatments and the page count question:
`references/rendering.md`.

## Phase 7: The cover letter

**Written last.** A letter written before the scoring is a letter about the person in
general. A letter written after it knows which of their evidence this advertisement
actually wants.

`cover-letter-<variant>.md`, in the person's folder. One page. Four to six paragraphs. It does the one job the
CV and the statement of claims cannot: why this person, for this job. If a paragraph
could be cut and nothing would be lost that the CV already says, cut it.

The letterhead is the CV's letterhead, taken from the same file so the two cannot
drift. The addressee, the position number and the contact's name come out of the job
pack, not a template.

Full instructions, including what earns a paragraph and what a keyword screener needs
from it: `references/cover-letter.md`.

```bash
D="$(python3 scripts/paths.py --data)"
python3 scripts/render_cv.py "$D/cv-<variant>.md" --letter "$D/cover-letter-<variant>.md" \
    --layout sidebar-dark --palette navy \
    --role "<the job title>" --employer "<the employer>" --pdf
```

Then build the studio once more with `--letter` added, so the letter can be marked up
the same way the CV was. The studio has a Resume and Cover letter chooser under
Document in the Skin tab. Both documents wear the same skin, because they are posted
together, and every line of the letter can be marked up exactly like a line on the CV.

**Done when:** it is one page, every claim in it traces to the record, and there is not
one defensive sentence in it.

---

## Fact alignment across variants

Once a person has more than one CV variant, they will drift, and a recruiter may see
two. Run `references/assembling.md`, section "Aligning variants", whenever a second
variant exists or an old one resurfaces.

One facts ledger, many variants. A fact resolved in one variant propagates to all of
them. Tailoring changes which facts print and how they are worded for an audience; it
never changes what is true.

---

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
| `references/atomising-sources.md` | Phase 2 |
| `references/scoring.md` | Phase 3 |
| `references/proposing-changes.md` | Phase 4, before writing any proposal |
| `references/assembling.md` | Phase 6, and whenever a second CV variant exists |
| `references/arithmetic.md` | Any time a number, date or year count is involved |
| `references/rendering.md` | Only if the person wants a designed CV or a report |
| `scripts/build_studio.py` | Phase 3, then rebuilt in 4 and 6: the studio, built from their CV |
| `scripts/paths.py` | Any time you need to know where this person's files go, and in every command that names one |
| `scripts/documents.py` | Phase 1, before anything else: what they have already produced |
| `references/rewriting.md` | Before drafting any suggested line: the shape, the verb, and the named patterns to demonstrate on the person's own lines |
| `references/ats.md` | Before handing over any PDF: what the screener actually gets |
| `references/marking.md` | Before touching the studio's per-line decisions |
| `references/achievements.md` | Before drafting key achievements or adding a section |
| `references/cover-letter.md` | Phase 7, before writing a line of the letter |
| `templates/` | Shapes for facts, answers, asks, proposals, scorecard, achievements, cv |
| `scripts/check.py` | Run it, with no arguments, at the end of Phase 4 and the end of Phase 6 |
| `scripts/render_cv.py` | Optional final step: markdown CV to printable HTML, 900 skins |
| `scripts/render_report.py` | Only if they ask for the score as a page of its own. The studio is the scorecard |
| `scripts/to_pdf.py` | The print engine. Never called directly; `--pdf` uses it |
| `scripts/fetch_fonts.py` | Once, on a machine with internet, so PDFs stop needing one |
| `assets/skins.json` | Layouts, palettes and typesets. Add one by adding a row |
