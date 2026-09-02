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

# 4. MISSING AND WORTH ADDING

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

# 5. WORDING

---

# 6. NO CHANGE NEEDED

What was checked and deliberately left alone, so nothing looks overlooked.
