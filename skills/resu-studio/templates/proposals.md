---
job: employer-role-title
variant: cv-data-reporting
written: YYYY-MM-DD
budget:
  role-example: 8 bullets
  skills: 8 group lines
  pages: 3
---

# Proposals

Full current text and full replacement text on every entry.

**Every entry carries a `Line:`**, the studio's id for the line it lands on, from
`references/marking.md`. That id is what puts the suggestion on the right line of
the page when the studio is built with `--proposals`. An entry without one never
reaches the person, and so does an entry naming an id this CV does not have:
`build_studio.py` names both on the way past.

**The ids belong to the CV the studio was built from.** Ids are positional, and
`scripts/assemble.py` reorders and removes lines in Phase 6, so after the assembly every
id here names a line of the assembled document. Every entry in this file gets a
`Decision:` before the assembly runs. Anything raised after it goes into a new studio
built from `cv-<variant>.md`, where the ids and the page agree again.

The `## P1.` heading carries the location, in words. Everything else is a bold field:

```
Line          the studio's id for the line this lands on
Currently     the full existing text, verbatim, or `Not on the CV.`
Suggested     the full replacement text, or `Delete this bullet.`
Why           one or two sentences
Answers       which ask ids this serves
Draws on      which fact ids this rests on
Costs         on an addition, which line comes out or how the budget rises
Decision      left blank for the person
```

---

# 1. FIX BEFORE SENDING

## P1. Section, role, which bullet

**Line:** professional-experience/0/b2
**Currently:**
The complete existing text, verbatim.

**Suggested:**
The complete replacement text, ready to paste.

**Why:** One or two sentences.

**Answers:** a1, a4
**Draws on:** fact-id, fact-id
**Decision:**

---

# 2. DECIDE

Places where a fact only the person has is needed. State both options in full where
there are two.

---

# 3. SAME CLAIM TWICE

## P8. Section, role, which bullet

**Line:** professional-experience/1/b0
**Currently:**
The complete existing text.

**Suggested:**
Delete this bullet.

**Why:** Names the other place the claim already appears, quoted, and says why that
copy is the one to keep.

**Decision:**

---

# 4. CUT THIS TO MAKE ROOM

A line that answers nothing this advertisement asks for, on a page that is full.
`references/rewriting.md` names this as one of the three shapes a useful change takes,
and it is the only one that produces a proposal with no replacement text.

**This is not the same as group 3.** There the claim is on the page twice and one copy
goes. Here the claim appears once, it is true, and it is spending a slot that a line
answering a criterion needs. So the reason has to name what goes in its place, and the
person can accept the cut and refuse the replacement, or the other way round.

Where the page has room, there is no cut to propose. Say so in group 7 rather than
finding one.

## P10. Section, role, which bullet

**Line:** professional-experience/1/b2
**Currently:**
The complete existing text.

**Suggested:**
Delete this bullet.

**Why:** What this advertisement asks for that this line does not touch, and which
proposal takes the slot.

**Costs:** frees one bullet in this role, taken by P12

**Decision:**

---

# 5. MISSING AND WORTH ADDING

## P12. Section, role, where the new line goes

**Line:** professional-experience/0/b3
**Currently:** Not on the CV.

**Suggested:**
The complete new line.

**Why:** What it answers and why it is worth a slot.

**Costs:** which existing line comes out, or "budget rises from 8 to 9, confirm"

**Answers:** a7
**Draws on:** fact-id
**Decision:**

---

# 6. WORDING

---

# 7. NO CHANGE NEEDED

What was checked and deliberately left alone, so nothing looks overlooked.
