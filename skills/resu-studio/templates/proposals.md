---
job: employer-role-title
variant: cv-<audience>
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
Kind          which kind of change this is, from the list below
Line          the studio's id for the line this lands on
Currently     the full existing text, verbatim, or `Not on the CV.`
Suggested     the full replacement text, or `Delete this bullet.`
Why           one or two sentences
Answers       which ask ids this serves
Draws on      which fact ids this rests on
Costs         on an addition, which line comes out or how the budget rises
Decision      left blank for the person
```

**The entries run in page order, top to bottom.** Sections in the order the CV sets
them out, roles in the order they appear inside a section, bullets in the order they
appear inside a role, skills groups in the order they are drawn. They are numbered P1
upward in that same order, so the number in the chat and the position on the page agree.
Every suggestion is read in the studio on the line it would change, and a file in any
other order makes the person hunt.

The kinds, which `Kind:` names and which no longer decide where an entry sits:

- `fix before sending`, a factual error, a tense left behind after a date change, or a
  claim the record does not support.
- `decide`, a place where a fact only the person has is needed. State both options in
  full where there are two.
- `same claim twice`, where the claim is on the page twice and `Why:` quotes the other
  copy.
- `cut this to make room`, where the claim appears once, is true, and is spending a slot
  a line answering a criterion needs.
- `missing and worth adding`, with where it goes.
- `wording`, where the claim and its evidence stand and the line says them less well
  than it could.
- `no change needed`, which takes no number and goes at the foot of this file.

Full rules for all seven: `references/proposing-changes.md`.

---

## P1. Section, role, which bullet

**Kind:** fix before sending
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

## P2. Section, role, where the new line goes

**Kind:** missing and worth adding
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

## P3. Section, role, which bullet

**Kind:** same claim twice
**Line:** professional-experience/1/b0
**Currently:**
The complete existing text.

**Suggested:**
Delete this bullet.

**Why:** Names the other place the claim already appears, quoted, and says why that
copy is the one to keep.

**Decision:**

---

## P4. Section, role, which bullet

**Kind:** cut this to make room
**Line:** professional-experience/1/b2
**Currently:**
The complete existing text.

**Suggested:**
Delete this bullet.

**Why:** What this advertisement asks for that this line does not touch, and which
proposal takes the slot.

**Costs:** frees one bullet in this role, taken by P2

**Decision:**

---

# NO CHANGE NEEDED

What was checked and deliberately left alone, so nothing looks overlooked. These have no
change to sit on a line, so they take no `P` number and stay here at the foot of the
file. Where the page had room and there was no cut to propose, say that here rather than
finding one.
