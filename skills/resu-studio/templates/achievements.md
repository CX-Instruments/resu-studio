---
job: employer-role-title
variant: cv-<audience>
written: YYYY-MM-DD
---

# Key achievements

Six drafted lines, written at career level, for the person to pick from in the studio.
`build_studio.py --achievements achievements.md` loads them into the Key achievements
panel under Sections. Nothing prints until they tick it.

**Each line reaches across more than one employer.** A line condensed out of a single
role bullet says the same thing twice on one page, and if that bullet is later removed
the achievement is left with no job behind it. Full rules: `references/achievements.md`.

**Draft six and let them pick.** Six is a real choice where ten is a chore. They tick
four to six, and ticking four is the common landing. If a sixth line only exists to
reach six, it comes off. Picking for them is never the job.

```
id: k1
text: "The line, exactly as it would print. One sentence."
answers: a2, a7
draws_on: Employer One, Employer Two, Employer Three
```

```
id: k2
text: "The second line. A different span of the record, not a rephrasing of the first."
answers: a1, a4
draws_on: Employer One, Employer Four
```

```
id: k3
text: "The third."
answers: a3
draws_on: Employer Two, Employer Three
```

```
id: k4
text: "The fourth."
answers: a5, a6
draws_on: Employer One, Employer Three
```

```
id: k5
text: "The fifth."
answers: a8
draws_on: Employer Two, Employer Four
```

```
id: k6
text: "The sixth."
answers: a9
draws_on: Employer One, Employer Two
```
