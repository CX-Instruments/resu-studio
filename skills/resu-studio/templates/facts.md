---
person: Full Name
updated: YYYY-MM-DD
variants:
  - CV 2026 condensed
  - CV 2026 full
---

# Facts

One entry per atomic claim, in the person's own words. This ledger is reused for
every application. Most of what is here will not print on any given CV.

## role-example

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

## example-bullet

```
id: example-bullet
kind: bullet
parent: role-example
sources:
  - cv: CV 2026 condensed
    section: Example Employer, Key Responsibilities, bullet 6
    text: "Their exact words, verbatim, from this document"
  - cv: CV 2026 full
    section: Example Employer, Key Responsibilities, bullet 7
    text: "Their exact words from the other document, where they differ"
figures: []
confirmed: false
conflict: false
```

## example-conflict

```
id: skill-example
kind: skill
group: Example skills group
sources:
  - cv: CV 2026 condensed
    text: "A skill (Advanced)"
  - cv: CV 2026 full
    text: "A skill (Master)"
confirmed: false
conflict: true
conflict_note: "Two levels for the same skill. The person decides. Do not pick."
```

## example-stated

```
id: fact-team-size
kind: bullet
parent: role-example
sources:
  - stated: "by the person, 2026-08-28"
    text: "The team was one DBA and two analysts"
figures: ["1 DBA", "2 analysts"]
confirmed: true
conflict: false
```
