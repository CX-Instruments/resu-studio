# Correct method for testing rewrite positioning

Date: 18 September 2026  
Status: proposed replacement for the invalid direct-rewrite tests

## Why the previous tests are invalid

The plugin does not ask a model to regenerate a complete CV freely. It:

1. preserves the source CV
2. builds the factual and employer records
3. scores before changing anything
4. proposes changes against real line IDs and fixed budgets
5. lets the person decide
6. assembles only those decisions while copying every other line through unchanged

The previous test prompt skipped that contract and requested a complete rewritten CV.
The models consequently changed section order, headings, skill grouping, punctuation
and level presentation. Those changes were not caused only by positioning and would not
normally survive the proposal and assembly controls.

The skill contract already requires:

- skill levels to remain exactly as the person wrote them
- levels to print as `item (Level)`
- every change to appear as a proposal
- every untouched line to copy through unchanged
- the assembler, rather than the language model, to produce the final CV

## What the corrected A/B must isolate

The only treatment difference should be:

- **A:** Phase 4 reads proposing and rewriting rules without `positioning.md`
- **B:** Phase 4 reads the same rules plus `positioning.md`

Everything else must be byte-identical: source CV, facts, answers, asks, scorecard,
line IDs, bullet budgets, model, prompt and validation.

The supplied Northside scorecard must first be corrected so the 2025 First Aid entry
does not become a claim of current currency.

## Test artifact

The primary output should be `proposals.md`, because that is the plugin's real rewrite
output before the person decides. Do not ask either condition to write a finished CV.

For every permitted line, present:

| Field | Purpose |
|---|---|
| Line ID | Proves both conditions are changing the same slot |
| Current | Exact source text |
| A suggestion | Old-rule rewrite, or no change |
| B suggestion | Positioning rewrite, or no change |
| Why | What the proposed change buys the reader |
| Draws on | Exact fact IDs |
| Answers | Exact employer ask IDs |
| Costs | Addition, removal or no budget change |

The Skills block should remain byte-for-byte unchanged unless a separate, explicit
proposal changes it. Any skill proposal must preserve `Advanced`, `Intermediate` and
`Working knowledge` exactly and keep the parenthesised form.

## Conformance gate before quality scoring

Exclude and rerun an output if any of these fail:

- proposal template parses
- every proposal has a real line ID
- current text matches the source exactly
- every suggested claim traces to facts
- levels and figures are unchanged unless the source supports the change
- the bullet budget balances
- no claim appears twice
- `check.py` exits 0
- the Studio can place every proposal on its source line

An invalid output receives no four-pillar score. It is a harness or instruction failure,
not evidence that one condition writes better.

## Four-pillar assessment

Score the valid proposals, not a freely regenerated document.

| Pillar | Test question |
|---|---|
| Motivation | Did the condition recognise what work the person wants more of, or ask the one question needed to establish it without inventing passion? |
| Strengths | Did it identify repeated, proved contribution patterns rather than rewrite isolated duties? |
| Differentiated value | Do the profile and evidence choices make one useful combination clear without a slogan? |
| Proof of impact | Did it select and preserve supported result, scale, difficulty, responsibility or beneficiary evidence? |

Truth, ATS relevance, human voice, non-salesy restraint, duplication and format
preservation are mandatory gates around the pillar score.

## How to show the result

The review document should start with the literal proposal comparison table. It should
then show:

- conformance result for every run
- four-pillar score for every valid run
- the same lines assembled under a declared test-only decision policy, if a complete CV
  view is still useful
- variability across at least three GPT-5.6 Sol runs per condition

Pair numbers should not be interpreted individually. Without a deterministic seed,
the decision is based on the distribution of valid outputs and recurring differences,
not whether A or B happened to be more detailed in one pair.
