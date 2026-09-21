# Writing-mode transitions ? 21 September 2026

The owner requested seamless switching, less repeated generation, and replacement
of a revised personal-mode option without losing earlier rewritten work. They
confirmed that manual edits and explicit keep decisions should remain by default,
with mode-related alternatives offered as suggestions.

## Implemented behaviour

- Importing a mode request saves the current partial review, including undecided
  suggestions, personal edits, keeps, additions and ordering.
- A matching saved round is restored when its CV, guiding brief, mode definition,
  relevant evidence and job pack still match. Outstanding requests for another
  wording prevent reuse of that round.
- Otherwise the previous round and current decisions inform new work. The agent
  can submit changed proposals and reference unchanged UIDs in `reuse_proposals`.
  Publication validates the combined result.
- Current user wording remains on the CV. New proposals compare against that
  effective wording. Identical suggestions with unchanged supporting evidence
  can retain decisions; different wording does not inherit approval.
- A changed personal brief updates the existing comparison slot and versions its
  definition. Earlier definitions, samples and rewrite batches remain saved.
  Creating a separate additional option requires explicit `keep_custom_modes` intent.
- After assembly, the next request uses the finished current CV as its source.
  An earlier round on a different source is not blindly reinstated.

## Storage and context cost

The existing `writing.json` and `.writing` history are used; no folder per mode or
new model service is added. Batches retain generated records and partial decisions.
A fresh browser can restore the captured review from disk. Local edits made after
sending a request are also preserved during the next rebuild.

Normal command output contains current context, one active batch and compact
history summaries. It omits the full historical batch array. `writing.py history`
lists saved rounds; `writing.py context --batch <id>` retrieves one earlier round.
The workflow no longer immediately reads the same context after importing it.

This avoids repeated generation for matching rounds and repeated historical prose
in normal context. It is not a measured token-saving claim. Changed sources or a
new definition may require new writing; semantic quality still needs host review.

## Verification

All eight repository suites passed: 210 existing checks and 14 writing lifecycle
and browser tests. New coverage includes A-to-B-to-A reuse, late manual edits,
fresh-browser restoration, relevant versus unrelated evidence changes, changed
CV sources, replacement of a custom slot while retaining the old round, unchanged
proposal reuse, and continuing from an assembled CV. A drawer obstruction found
when returning from review to Writing was fixed and covered by the browser flow.

JavaScript syntax and final diff whitespace checks passed. Test artifacts stay
under ignored `.work`. The external test environment was not modified.
