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
python3 scripts/build_studio.py --cv "cv-<variant>.md" --role "<the job title>" \
    --facts "$(python3 scripts/paths.py --facts)"
```

`paths.py` has one flag per path, each printing one bare line and nothing else:
`--data`, `--facts`, `--answers`, `--documents`, `--cv-source`. Run it with no argument
to see the folder it resolved and why.

## What counts as one fact

One claim, one entry. A role paragraph containing three claims is three facts with
the role as parent. A bullet that says two things is two facts if they can be
separated and used independently, one if they cannot.

The test: could this appear on a page on its own and mean something?

## The entry

```
id: redgate-liaison
kind: bullet
parent: role-redgate
sources:
  - cv: CV 2026 condensed
    section: Redgate, Key Responsibilities, bullet 6
    text: "Liaised with Rates, Property, Compliance, and Waste stakeholders to clarify data requirements, validate business rules, and ensure migrated data supported current and future operational processes"
  - cv: CV 2026 v2
    section: Redgate, Key Responsibilities, bullet 7
    text: "Liaising with business stakeholders across Rates, Property, Compliance, and Waste teams to clarify data requirements, validate business rules, and ensure migrated data reflects current and future operational processes in CiA"
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
title: Data Intelligence Specialist
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

A fact the person told Claude rather than wrote down has a `stated:` source instead of
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
text: "experience leading the development of <the thing the advertisement names> using <the tools it names>r BI or similar tools, and translating complex data into actionable insights for decision-makers"
necessity: must
where: "Job pack, Our ideal candidate"
group: tool
```

**`necessity` has five values**, the same five `templates/scorecard.md` allows and the
same five the studio labels:

| value | what it is | how the studio labels it |
|---|---|---|
| `must` | the advertisement says it is required | Essential |
| `nice` | the advertisement would like it | Desirable |
| `implied` | not stated, and traceable to a specific sentence | From the role description |
| `condition` | a requirement of being employed at all: citizenship, a licence, a clearance | A condition of the job |
| `not a cv question` | in the ad, and settled somewhere other than the document | Not a CV question |

`condition` and `not a cv question` used to be folded into `implied` on the way into the
studio, which showed a hard eligibility bar as a soft item lifted off the role
description. They are their own values and they stay their own values.

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

Where an advertisement publishes criteria the application is expected to answer,
under whatever name, whether selection criteria, essential criteria, key requirements
or person specification, every one is a
`must` and the exact heading goes in `where`. In those sectors, failing to visibly
address one criterion generally excludes the application.

## Implied asks

Some of the hardest filtering happens on things the advertisement plainly needs and
never states. Citizenship for an ongoing public service role. Domain knowledge of the
thing the whole branch exists to do. Write these in your own plain words, because
there are no words of theirs to quote, and put the sentence you inferred it from in
`where` so the person can argue with the inference.

Be disciplined. An implied ask is traceable to a specific sentence. It is not a guess
about what employers generally like.

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
