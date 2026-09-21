# Phase 1 in full: sources, and how deep to go

SKILL.md carries the short version of Phase 1. This is the whole of it, with every
reason behind each rule. Read it at the start of Phase 1, before copying anything in.

## First: where their files live, and which job this is

**First resolve the current task workspace**, following `where-files-go.md`. The default
is exactly `Resu - CV Builder` there. Status does not scan old locations; initialise
the default without an extra folder-choice question.

**Use only supplied or explicitly designated sources.** Resume an existing application
only when requested. Do not inspect old outputs, another job's evidence or saved shared
history to prepare a fresh application. A fresh-start instruction changes source scope,
not the standard destination. Do not invent a sibling folder or workflow. Previous-session claims or model memory are not source evidence: verify against this application's authorised files or the user's current statements.

**Then start the job**, with the role and the employer written the way the advertisement
writes them, and its link and closing date when you have them:

```bash
python3 scripts/jobs.py new --role "<the job title>" --employer "<the employer>" \
    --link "<the ad's URL>" --closes YYYY-MM-DD
```

It refuses a second open job for the same role at the same employer and names the one that
exists. Resume it only if requested. An explicit fresh-start request authorises `--again` on `jobs.py new`, creating a separate job inside the same standard root. Otherwise ask which of those two actions they want. It prints the job id, and every command for this application
passes it as `--job <job id>` from here on. The start of the id is enough while only one
job starts that way.

**Each application owns its evidence.** `facts.md` and `answers.md` live in its job
folder, alongside `asks.md`. Build them from authorised inputs. Shared saved records
are optional sources only when explicitly requested. For an explicitly resumed older
application, copy its authorised ledger into the job folder before continuing. Every
job's finished documents stay in its own folder under `4 Finished documents`.

**Never pass one job's id while working on another.** That is the one thing that would put
one employer's answers in another employer's folder.

**Copy the advertisement, and the job pack if there is one, into the job's `ad` folder**,
untouched: `python3 scripts/paths.py --job <job id> --job-ad` names it. **Copy every CV
variant into `1 About me`**, which `python3 scripts/paths.py --about` names, using only files authorised for this application. Preserve existing originals; if a supplied filename collides, keep its new copy inside the active job folder. A LinkedIn URL or any other link the person shares goes
into `links.md` in the same folder, one per line. Extract the text of each file into a
`.txt` beside it, so a later session can re-read without the original.

**Then write the CV out as markdown in the `templates/cv.md` shape, into
the active job folder.** Nothing later in this skill can read a PDF or a Word file. Phase 3
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

**Done when:** the job exists, the advertisement is in its `ad` folder in the person's own
words, the CV is saved in the job folder as markdown in the `templates/cv.md` shape with a `# Name` heading at the
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

If the user has already specified the scope, record it and continue. Otherwise ask it plainly, in these terms, and wait for an answer:

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

**Record the answer the moment it arrives**, like every other answer. It goes in twice.
On the job, with `python3 scripts/jobs.py set <job id> depth essentials` (or `all`), because
depth belongs to this advertisement and the next one is asked again. And in `answers.md` as a
normal `q:` and `a:` block carrying a `depth:` field of its own, naming the job, so what was
asked and what they said is on the record like every other question. The word is
`essentials` or `all`.

The scorecard does not exist yet. When it is written in Phase 3, copy the same word into
its frontmatter as `depth:`, which is where `build_studio.py` reads it and where every
later session finds it without asking again.

**Never choose for them, and never quietly do the bigger job.** If they have not
answered, ask again rather than assuming. Doing the full pass uninvited spends someone
else's limit on a decision they did not make.
