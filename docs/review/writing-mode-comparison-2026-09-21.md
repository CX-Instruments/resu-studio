# Writing comparison and personal-mode refinement

Implemented on `review/cv-rewrite-strategy`, within `D:\resu-plugin`, following the owner's test of the first rewrite-engine build. The supplied test Studio was read for diagnosis; its files were not changed.

## What the test revealed

The first two roster bullets differed mainly in verbs and compression. All four profiles had similar openings, making their different emphases harder to notice. The expressive bullet's claim of "reliable coverage" also exceeded a source that established fewer gaps. Stronger variation must preserve factual precision, not introduce a more flattering outcome.

The former two-column cards each repeated both original passages. Comparing one passage meant reading past unrelated content and scrolling between rows. Personal-mode creation was a hidden disclosure with two unstructured fields.

## Changes

| Agreed requirements | Implementation |
|---|---|
| R01, R03, R26: integrated exploration and meaningful comparison | One original profile and one original bullet. Opening either reveals that passage's mode versions; the other comparison closes. Four built-ins share one desktop row. On narrow screens, version buttons replace the passage in the same position without selecting it for generation. |
| R02, R04–R08, R15, R21–R23: distinct modes with shared quality | Built-ins are version 2 with specific information-order, emphasis and rhythm preferences. The preparation instructions require a pairwise contrast review and a factual recheck. Each passage can explain its actual difference. Identical profile/bullet pairs are rejected; near-copy quality remains a semantic review responsibility. |
| R23–R25: personal guiding briefs with clear scope | A visible builder offers a starting mode, optional emphasis/voice/rhythm choices, free-text direction and things to avoid. A live plain-language brief shows what will be requested. Saving a reusable mode requires an explicit checkbox and name; otherwise the preview stays application-specific. |
| R03, R26–R27: explore, then authorise once | Preview requests generate samples only. `preview_mode` highlights the returned option; `preview_base` keeps the starting option beside it. A subsequent rewrite selection takes precedence over that preview. The existing single rewrite action and review handoff remain in place. |
| R24 and revision continuity | Browser drafts survive reloads and rebuilt previews. Unsent builder preferences do not modify a selected built-in rewrite. Source invalidation and pending requests disable writing controls. Mode definitions already saved in applications remain their original snapshots. |
| R16–R20: full-document execution | The engine instructions now explicitly compare representative full-CV passages with the chosen samples during the engagement/coherence review, without imposing one formula on every bullet. |

## Validation and limits

All eight repository test suites passed: 210 existing checks and eight writing lifecycle/browser tests. Added checks cover a single desktop comparison row, switching passages without losing selection, builder handoff contents and scopes, saved drafts, idempotent requests, returned preview ordering, mobile browsing versus selection, pending/stale controls and duplicate sample rejection. Browser screenshots were inspected in light and dark themes and at phone width. JavaScript syntax and `git diff --check` passed.

This is a local HTML interface: the live builder preview is the guiding brief, not generated CV prose. The person sends one handoff to the host AI to obtain new samples. No external service or runtime dependency was added.

The host AI still writes and judges the prose. Stronger instructions and duplicate rejection do not constitute evidence that every future response will differentiate the modes well. Existing generated HTML embeds its old UI and sample snapshots: rebuild to get the interface, and prepare fresh samples to apply version 2 mode definitions. A repo-local interface preview under ignored `.work` uses the supplied Studio's existing wording and labels that limitation explicitly.
