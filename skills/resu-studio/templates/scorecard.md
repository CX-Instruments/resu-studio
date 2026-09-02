---
job: employer-role-title
variant: cv-data-reporting
scored: YYYY-MM-DD
stage: before
verdict: worth it
counts:
  asks_total: 0
  must: 0
  nice: 0
  implied: 0
  you_have: 0
  a_reader_would_find: 0
  not_yet_worked_out: 0
---

The honest answer in one sentence, written to them, no heading above it.

**What is missing.** Gaps first, plainly, unsoftened.

**What is partial.** What they have and what was asked, side by side.

**What is there but invisible.** The employer's words and the person's words, and the
statement that they are the same work. This is the most valuable section.

**What is confirmed.** Short. Confirmation is not news.

**The two counts.** What you have, what a reader would find, and the one sentence
explaining why they differ.

---

# Ask by ask

**Every row needs all five cells, even when one is empty.** The columns are read by
position, so a missing cell shifts every later cell one to the left: the state lands
under Necessity, the evidence lands under State, and the report either refuses or, if
anything slips past, shows a bar chart that disagrees with its own gauges. An implied
duty with no stated necessity is still `implied`, not blank.

Necessity is one of: `must`, `nice`, `implied`, `condition`, `not a cv question`.

State is one of these seven words, and no others. They are the words the studio's
Score tab and the skill both use, so all three describe an ask the same way:

| state | means |
|---|---|
| `page` | On your CV. A line answers it, in wording close to theirs. |
| `buried` | On your CV, your wording. The work is there; their term for it is not. |
| `off` | Left off this CV. The record answers it and this variant does not carry it. |
| `near` | Half answered. Part is answered and nothing claims the rest. |
| `missing` | Nothing to say yet. Nothing in the record touches it. |
| `none` | Not a CV question. Handled outside the document. |
| `unscored` | Not checked yet. Nobody has set it against the record. |

The **Ask** cell starts with the id from `asks.md`, so the studio can put the
advertisement's own wording and the line that answers it side by side. The
**Evidence** cell is fact ids from `facts.md`, comma separated — that is where the
studio reads the verbatim line from.

| Ask | Necessity | State | Evidence | Note |
|---|---|---|---|---|
| a1 SQL across large datasets | must | page | fact-sql-2 | |
| a2 Stakeholder engagement | must | buried | fact-brief-1 | their word, your word |
| a3 Data governance | must | near | fact-gov-3 | what you have, what was asked |
| a4 Machine learning | nice | missing | | plainly |
| a5 | must | not yet worked out | | not a gap, nobody has checked |
