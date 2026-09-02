---
updated: YYYY-MM-DD
depth: essentials
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
`essentials` or `all`. It goes in two places in this file. In the frontmatter above, so
a later session finds it without reading the whole thing. And on the block that recorded
the question, as a sixth field, so what was asked and what they said stays on the record
like every other answer. Copy the same word into `scorecard.md`'s frontmatter in Phase 3,
because that is where `build_studio.py` reads it.

If they widen it later, append a second block carrying `depth: all` and use the newer
one, the same as any other changed answer, and change the frontmatter to match.

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
