---
job: employer-role-title
employer: Employer Name
title: Role Title As Advertised
closes: YYYY-MM-DD HH:MM TZ
confidence: high
sources:
  - Advertisement
  - Job pack
application:
  documents: []
  page_limit:
  word_limits: {}
  conditions: []
  disclosure:
---

# Asks

One entry per thing the advertisement asks of the person. Compound asks are split.

```
id: a1
text: "Their exact words, verbatim"
necessity: must
where: "Job pack, Our ideal candidate"
group: skill
```

```
id: a2
text: "Their exact words for the second subject in the same sentence"
necessity: must
where: "Job pack, Our ideal candidate, same bullet as a1"
group: experience
split_from: "the original compound sentence, quoted in full, once"
```

```
id: a9
text: "In your own plain words, because there are no words of theirs to quote"
necessity: implied
where: "Inferred from: 'the exact sentence you inferred it from'"
group: qualification
```

# What the employer says about itself

Recorded, never matched against the person. Sets the register of the writing and
nothing else.

```
id: v1
text: "Their words about their own culture or pace"
where: "About us"
```

# What made this hard to read

Anything that limited the reading, so `confidence` can be argued with.
