---
job: employer-role-title
variant: cv-data-reporting
scored: YYYY-MM-DD
stage: before
depth: essentials
verdict: worth it
counts:
  asks_total: 0
  must: 0
  nice: 0
  implied: 0
  condition: 0
  not_a_cv_question: 0
  you_have: 0
  a_reader_would_find: 0
  unscored: 0
---

**There is a count key for every necessity value, and all five are legal.**
`condition` and `not_a_cv_question` were missing here while the table below allowed
them, so a scorecard with a licence condition on it had rows the counts could not
describe. The count key is written with underscores, `not_a_cv_question`, because the
frontmatter reader takes a key of word characters. The word in the table stays
`not a cv question`, with the spaces, because that is what the studio reads.

The five necessity counts add up to `asks_total`. `you_have` and
`a_reader_would_find` are the two gauges and they count states rather than necessities,
so they are outside that sum. `render_report.py` prints these counts where they are
there and tallies the table only where they are not, so a count that disagrees with the
table is a report that disagrees with itself.

`depth:` is `essentials` or `all`, copied out of `answers.md` from the question put in
Phase 1. `build_studio.py` reads it straight from this frontmatter, so the studio can
say how deep the advertisement was scored without being told again.

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

Necessity is one of: `must`, `nice`, `implied`, `condition`, `not a cv question`, written
in the table with the spaces exactly as here.

`condition` is anything that is a requirement of being employed at all, a licence,
citizenship or a right to work, a clearance, **whether or not the advertisement published
it among its criteria**. `must` is a claim about capability that the application has to
evidence. `implied` covers a duty the advertisement states and does not list among its
criteria, as well as something it never writes down that a specific sentence gives away.
The rules and the reasoning are in `references/atomising-sources.md`.

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
**Evidence** cell is fact ids from `facts.md`, comma separated, and that is where the
studio reads the verbatim line from.

| Ask | Necessity | State | Evidence | Note |
|---|---|---|---|---|
| a1 SQL across large datasets | must | page | fact-sql-2 | |
| a2 Stakeholder engagement | must | buried | fact-brief-1 | their word, your word |
| a3 Data governance | must | near | fact-gov-3 | what you have, what was asked |
| a4 Machine learning | nice | missing | | plainly |
| a5 | must | unscored | | not a gap, nobody has checked |
