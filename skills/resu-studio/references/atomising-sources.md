# Atomising the sources

Two ledgers. The facts ledger describes the person and is reused forever. The asks
ledger describes one advertisement and is thrown away with it.

---

# The facts ledger

`facts.md`. One entry per atomic claim the person has made about their working life,
in their own words.

**It lives in the person's own folder, outside the plugin, so it is never named as a
bare relative path.** A relative path resolves against whatever directory the session
happens to be in, and that directory is thrown away at the end of the session.
`scripts/paths.py` prints the real one, and every command that passes it uses command
substitution so the file lands where the next session will find it:

```bash
python3 scripts/paths.py --facts
python3 scripts/build_studio.py --cv "cv-<variant>.md" --job <job id> \
    --facts "$(python3 scripts/paths.py --facts)"
```

`paths.py` has one flag per path, each printing one bare line and nothing else:
`--facts`, `--answers`, `--about`, `--jobs`, `--documents`, and `--job <job id>` for one
job's folder. Run it with no argument to see the folder it resolved and why. `facts.md` is
the person's, in `2 My record`; `asks.md` belongs to one advertisement and lives in that
job's folder, `"$(python3 scripts/paths.py --job <job id>)/asks.md"`.

## What counts as one fact

One claim, one entry. A role paragraph containing three claims is three facts with
the role as parent. A bullet that says two things is two facts if they can be
separated and used independently, one if they cannot.

The test: could this appear on a page on its own and mean something?

## The entry

```
id: firstrole-liaison
kind: bullet
parent: role-firstrole
sources:
  - cv: CV 2026 condensed
    section: <the employer>, Key Responsibilities, bullet 6
    text: "Their exact words, verbatim, from this document"
  - cv: CV 2026 v2
    section: <the employer>, Key Responsibilities, bullet 7
    text: "Their exact words from the other document, where the two differ"
figures: []
confirmed: false
conflict: false
```

`kind` is one of: `profile`, `role`, `bullet`, `achievement`, `skill`,
`qualification`, `education`.

**A `kind: role` entry carries the role's own fields instead of `sources[].text`**, so
a role can be printed without guessing at where its dates came from. From
`templates/facts.md`:

```
id: role-example
kind: role
title: <their job title>
employer: Example Employer
location: <city, country>
started: 2023-05
ended: 2026-06
display_dates: "2023 to 2026"
sources:
  - cv: CV 2026 condensed
    section: Experience, role 1, date line and heading
confirmed: true
conflict: false
```

`started` and `ended` are machine-sortable. `display_dates` is what the person wrote
and what prints, so "2023 to 2026" stays "2023 to 2026" and is never reformatted into a
range with a dash in it. A current role has no `ended`. Every bullet under the role
carries `parent: role-example`.

A `kind: skill` entry carries `group`, which is the heading the skill prints under, and
its level lives inside the source text in brackets rather than in a field of its own.

A fact the person told you rather than wrote down has a `stated:` source instead of
a `cv:` one, with who said it and when, and `confirmed: true`, because they said it.

## Read the bodies, not the headings

Most of what makes a CV strong for a particular job is in the third bullet of the
second-last role, or inside a paragraph that has never been broken into bullets. A
reading that takes job titles and a skills list can only ever answer the requirements
the person already knew they met.

## More than one CV variant is normal and it is the point

People keep a long one and a short one, and a version aimed at a different industry.
**The longer or older one usually holds the buried material,** because it was cut for
space rather than because it stopped being true.

Merge them into one ledger. Same claim from three documents is one fact carrying all
three wordings under `sources`. Keep every wording: one of them is likely to be the
language some future employer uses.

**Where two variants state the same fact differently, set `conflict: true` and record
both. Never pick.** The person decides. Two kinds of conflict matter:

- **Level conflicts.** The same skill at Master on one CV and Advanced on another.
- **Claim size conflicts.** "Developed, maintained and optimised" on one and
  "supported the development, maintenance and optimisation" on another. Those are
  different sizes of the same claim and the person has to choose which is true.

Conflicts drive both the questions in phase 4 and the alignment report.

## Skills need a grain decision, and the grain is the group

An earlier version of this workflow split a skills column into forty-five individual
skill entries. That is correct as a ledger and unusable as a page: a narrow skills
column cannot hold forty-five lines and the renderer silently clipped the overflow.

**In the ledger, one entry per skill, with its level and its group.**
**On the page, one line per group, with the skills comma separated inside it.** That
is how the person's own CV was written and it is what fits.

## Confirmed

`confirmed: false` on everything read out of a document. It becomes true when the
person has looked at it and said it is right. Nothing enforces this. It exists so a
later session can tell what has been checked from what has merely been extracted.

## What this step is not

Not a rewrite. Not an edit. Not a scoring exercise. Do not fix grammar, shorten
bullets or drop the 2009 role because it looks irrelevant. Relevance is decided per
advertisement, and the 2009 role is exactly the kind of thing that answers a
requirement nobody expected.

---

# The asks ledger

`asks.md`. One entry per thing the advertisement asks of the person.

```
id: a7
text: "experience leading the development of <the thing the advertisement names> using <the tools it names>, and <the second thing the same sentence asks for>"
necessity: must
where: "Job pack, Our ideal candidate"
group: tool
```

**`necessity` has five values**, the same five `templates/scorecard.md` allows and the
same five the studio labels:

| value | what it is | how the studio labels it |
|---|---|---|
| `must` | the advertisement names it as required, and the application is scored on it | Essential |
| `nice` | the advertisement would like it | Desirable |
| `implied` | in the role description and not on the scored list, or not written down anywhere and traceable to a specific sentence | From the role description |
| `condition` | a requirement of being employed at all: citizenship, a right to work, a licence, a clearance | A condition of the job |
| `not a cv question` | in the ad, and settled somewhere other than the document | Not a CV question |

`condition` and `not a cv question` used to be folded into `implied` on the way into the
studio, which showed a hard eligibility bar as a soft item lifted off the role
description. They are their own values and they stay their own values.

### `condition` beats `must`, even where the advertisement publishes it as a criterion

**The test is what kind of thing is being asked. Where it was printed does not decide
it.** A condition of employment is a yes or a no about the person's standing: they hold
the licence or they do not, they have the right to work or they do not. A `must` is a
claim about capability, which the application has to evidence and a panel has to weigh.

So a published criterion reading "must hold a current driver's licence" is a `condition`,
and it stays a `condition` even though the advertisement listed it among the criteria the
application is scored against. Marking it `must` puts a thing nobody can argue about into
the same count as the things the whole document exists to argue, and the score then moves
for a reason that has nothing to do with the writing.

Two things follow, and both matter to the person:

- **It still has to be visibly answered** where the sector's criteria have to be
  addressed one by one. `condition` is about how it is counted, and it does not excuse
  leaving it unanswered.
- **A condition they do not meet is not a gap to work on.** It is a reason the
  application will not proceed, and it is said plainly and early rather than scored.

### What separates `implied` from `must`

Both can be things the advertisement plainly states. **The line is whether the employer
put it on the list the application is scored against.**

- A duty in the role description, the duty statement or the position description, which
  the advertisement never lists among its criteria, is `implied`. It is stated in the
  employer's own words and it is still off the scored list, and it is worth answering
  wherever the record supports it.
- Something the advertisement never writes down at all but a specific sentence gives away
  is also `implied`. Domain knowledge of what the whole branch does, for one.
- Anything on the published criteria, the essential list, the person specification or
  whatever the employer calls the list it scores against, is a `must`.

The studio's label, "From the role description", is right for both halves of `implied`,
because both are read off the description rather than off the scored list. Put the
sentence it came from in `where` either way, so the person can see where it came from and
argue with it.

`group` is `experience`, `tool`, `skill`, `soft`, `qualification`, `other`.

**A split compound ask carries `split_from:`**, holding the original sentence quoted in
full, once, so the person can see what the seven asks were cut out of:

```
id: a2
text: "Their exact words for the second subject in the same sentence"
necessity: must
where: "Job pack, Our ideal candidate, same bullet as a1"
group: experience
split_from: "the original compound sentence, quoted in full, once"
```

Anything the employer says about itself goes in its own section of `asks.md`, with a
`v`-prefixed id, and is recorded rather than matched.

## Split compound asks

**This is the single most important instruction in this file.**

A duty that names seven subjects in one sentence is seven asks. Left whole, a person
who answers five of the seven reads as failing the entire thing, and the report tells
them they have a gap where they have a strength with two holes in it.

Split it, score each part, and the report can say "five of these seven are yours
outright, and here are the two that are not".

## Find the preferences the ad never labels

Some advertisements have a Desirable heading. Most fold preferences into prose. If
you only read the bulleted essential list you will miss half of what is actually
being weighed.

Read the whole thing, the role description, the About us, the last paragraph, and pull
out anything asked for in these words:

| Wording | Necessity |
|---|---|
| ideally, preferably, we would love, it would be great | nice |
| desirable, advantageous, beneficial, a plus, a bonus | nice |
| exposure to, familiarity with, some experience of, an understanding of | nice |
| you may have, you might bring, bonus points for | nice |
| experience with X or Y | nice for each, because either satisfies it |
| required, essential, must have, you will need, proven, demonstrated | must |
| N+ years, mandatory, you must hold, this role requires | must |

**The wording sets `must` or `nice`, and then the subject can override it.** "You must
hold a current C class licence" is written in the language of the `must` rows and it is a
`condition`, by the rule under the necessity table. Read what is being asked for before
reading how it was phrased.

Where an advertisement publishes criteria the application is expected to answer,
under whatever name, whether selection criteria, essential criteria, key requirements
or person specification, every one is a `must` and the exact heading goes in `where`.
In those sectors, failing to visibly address one criterion generally excludes the
application.

**With one exception, and it is the one above.** A published criterion that is a
condition of employment rather than a claim about capability is a `condition`. A licence,
a citizenship or right-to-work requirement, a clearance, a working-with-children check.
It still gets addressed in the application where the sector expects every criterion
addressed, and it is counted as what it is.

## Implied asks

`implied` covers two kinds of thing, and both belong to the role description rather than
to the scored list.

**A duty the advertisement states and does not list as a criterion.** The duty statement,
the accountabilities, the "what you will be doing" paragraph. These are stated in the
employer's own words, so quote them in `text` exactly as `must` entries are quoted, and
name the section in `where`. They are not `must`, because the employer did not put them
on the list the application is scored against. They are not `nice` either, because the
advertisement is not saying it would merely like them. They are the job, described.

**Something the advertisement never writes down and a specific sentence gives away.**
Domain knowledge of the thing the whole branch exists to do. Write these in your own plain
words, because there are no words of theirs to quote, and put the sentence you inferred it
from in `where` so the person can argue with the inference.

Be disciplined about the second kind. An inferred ask is traceable to a specific sentence.
It is not a guess about what employers generally like.

Where an ongoing public service role plainly needs citizenship and never says so, that is
a `condition` rather than an `implied`, by the rule above: it is a fact about the person's
standing, and inferring it does not change what kind of thing it is.

## What the ad says about itself is not an ask

Values, culture statements, how the team describes its own pace. These set the
register of the writing and nothing else. They never become something a person is
scored against, and a person is never matched against them.

## Say how well it read

Set `confidence` on the ledger to high, medium or low. Low is a normal outcome for
four sentences of adjectives, and saying so is more useful than a thorough-looking
list squeezed out of nothing. Record what made it hard.

## The application format is part of the ad

Capture it explicitly, because it changes the deliverables. It lives in the frontmatter
of `asks.md`, nested under `application:`, exactly as `templates/asks.md` sets it out.
`closes` is the one that sits at the top level, beside `employer` and `title`, because
it is a fact about the advertisement rather than about the paperwork:

```yaml
---
job: employer-role-title
employer: Employer Name
title: Role Title As Advertised
closes: 2026-08-31 23:30 AEST
confidence: high
sources:
  - Advertisement
  - Job pack
application:
  documents: [tailored CV, statement of claims, referee details]
  page_limit: 3
  word_limits: {statement: 800}
  conditions: [citizenship or right to work, security clearance]
  disclosure: "AI use must be disclosed"
---
```

A key with nothing to put in it stays, empty. The template ships them all empty for
that reason: a missing `page_limit` reads as "there is no page limit" and an empty one
reads as "nobody has found one yet", and those are different.

If the ad references a job pack and the pack is not in hand, stop and ask for it
before proposing anything. The pack routinely changes the deliverable, the length,
and the eligibility.
