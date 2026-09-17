# Phase 1 in full: sources, and how deep to go

SKILL.md carries the short version of Phase 1. This is the whole of it, with every
reason behind each rule. Read it at the start of Phase 1, before copying anything in.

## First: is there already an application in progress?

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

## Then stop and ask how deep to go. Before you read anything else.

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

**Record the answer in `answers.md`, the moment it arrives**, like every other answer.
It goes in twice, and `templates/answers.md` shows both places: as a `depth:` line in the
file's frontmatter, so a later session finds it without reading the whole file, and as a
normal `q:` and `a:` block carrying a `depth:` field of its own, so what was asked and
what they said is on the record like every other question. The word is `essentials` or
`all`.

The scorecard does not exist yet. When it is written in Phase 3, copy the same word into
its frontmatter as `depth:`, which is where `build_studio.py` reads it and where every
later session finds it without asking again.

**Never choose for them, and never quietly do the bigger job.** If they have not
answered, ask again rather than assuming. Doing the full pass uninvited spends someone
else's limit on a decision they did not make.
