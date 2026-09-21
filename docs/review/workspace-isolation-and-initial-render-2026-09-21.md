# Workspace isolation and initial Studio rendering

The current release is repaired without reverting the writing engine. This review uses only synthetic fixtures and records no applicant data from the reported screenshots.

## Causes and changes

- Folder resolution previously consulted installation/global records and host data variables. Status also searched legacy locations. Resolution now defaults to the actual task workspace plus the fixed `Resu - CV Builder` name. Alternative locations require a recorded explicit instruction scoped to that workspace. Status is read-only and does not discover older work.
- New writing preparations previously used the shared facts file. Writing and checking now require the active application's facts. Instructions use job-local facts/answers, explicitly authorised sources and the existing ordered workflow. Fresh work never creates a sibling root or silently resumes an existing application.
- Browser keys based on a root and human-readable job ID could recur after deleting and recreating the same application. New jobs now receive a random persistent instance ID, reused on rebuild and replaced on recreation. Compatibility builds without a job also have isolated identities. No legacy role/employer store is offered for automatic restoration.
- The Writing and Score tabs hid the iframe with `display:none` while pagination measured it. A long source reproduced one clipped sheet. The preview now uses `visibility:hidden` to remain measurable, and the parent resizes it when pagination reports completion.

The v0.6.0 comparison showed that role/employer browser keys and install-based folder selection predated the writing-mode release. The hidden Writing preview exposed a distinct first-load pagination regression. No rollback was made.

## Regression coverage

- Workspace defaults, no legacy discovery, explicit alternatives/imports, no cross-workspace redirection and private git-ignore behaviour.
- A new application's missing facts cannot fall back to shared history.
- Thirty artificial browser decisions survive a rebuild of the same synthetic application. Deleting only its verified temporary data root and recreating the same role, ID and output path produces zero pending decisions and zero proposals at writing-mode selection. The old browser key remains untouched.
- Multi-page content is paginated while Writing is open, before any Design click. Default, tinted sidebar, first-page sidebar and compact layouts retain the final source paragraph and sufficient iframe height without a redraw.
- Existing writing selection, approval, assembly, profile, browser launch, Desk, job, PDF text order and documented-command suites remain in the release checks.

## Upgrade behaviour

Install the corrected plugin/skill and rebuild the application's generated Studio. Existing HTML embeds its previous interface. Do not delete the user's application data or clear browser storage. Earlier browser-only state is not automatically imported across the new identity boundary; explicit same-application decisions already stored in writing state remain available.

## Verification outcome

All ten suites passed. The full runner exposed a repeat-run problem in the jobs test fixture: its cleanup still named the former test folder after the workspace change. The test now allocates a unique temporary root and its 34 checks passed on rerun. No product behaviour was relaxed to make it pass.

Writing: 24 tests; launcher: 4; PDF text order: 2; Python discovery: 8 checks; jobs: 34; job builds: 23; Desk: 52; workspace isolation: 9; end-to-end: 29; documented commands: 19. Four critical browser/source tests passed again against the extracted v0.7.2 package without skips. The package matches the source, and Python/JavaScript syntax checks passed.
