---
updated: YYYY-MM-DD
---

# Answers

Every question put to the person, and what they said. Read this before asking
anything. A question already in this file is never asked again, including one answered
with a "no", a "not sure", or a "rather not say".

This file lives beside `facts.md` in the person's own folder, so it carries from one
job advertisement to the next. `answers.md` records that the question was asked;
`facts.md` records what turned out to be true. `led to:` points from one to the other.

If an answer changes, append a new block rather than editing the old one, and use the
newer one. What they said and when is part of the record.

## The scoring depth has a field of its own

`depth:` is how far the person asked you to take the scoring, and it is either
`essentials` or `all`, and it belongs to one job ad, so every new ad is asked again. Record
it on the job with `python3 scripts/jobs.py set <job id> depth <word>`, and here, on the
block that recorded the question, as a sixth field with the job named in the question, so
what was asked and what they said stays on the record like every other answer. Copy the
same word into that job's `scorecard.md` frontmatter in Phase 3, because that is where
`build_studio.py` reads it. The `depth:` line in the frontmatter above is from before jobs
had folders; leave an old one alone and do not add one.

If they widen it later, append a second block carrying `depth: all`, use the newer one, and
set it on the job again.

```
q: Before I go through this, how far do you want me to take it? The must-haves only,
   or everything it asks for?
a: Just the must-haves for now, I want to know whether it is worth applying.
on: 2026-08-27
phase: 1
depth: essentials
led to: nothing
```

```
q: How many analysts were on the team? The line is much stronger with the number.
a: One DBA and two analysts.
on: 2026-08-28
phase: 4
led to: fact-team-size
```

```
q: Your file says you managed the consultant. Did you direct the partner's work, or
   coordinate with them?
a: Coordinated. I had no authority over their people.
on: 2026-08-28
phase: 4
led to: role-example
```

```
q: The ad asks for Python. Is there any Python on the record I have missed?
a: Not really. What there is was AI-written and I would not claim it.
on: 2026-08-29
phase: 3
led to: nothing
```

## Still unanswered

Questions that were put and not answered. These may be asked once more, named as
unanswered. Move the block up into the list above the moment an answer arrives.

```
q: Example of a question they have not come back on.
asked: 2026-08-29
phase: 4
```
