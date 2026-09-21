# Rewrite engine build and agreement trace

Built in `D:\resu-plugin`, on `review/cv-rewrite-strategy`, following the owner's
instruction to begin implementation. No install, release, deployment or comparative
writing evaluation was performed. Earlier branch edits and review documents remain.

## What is implemented

The Studio opens on a full-width Writing view, with the application case, its guiding
brief and comparable source/profile/bullet samples. Four built-in modes are included:
credible conviction, direct and focused, warm and grounded, expressive and distinctive.
Personal modes can be explored conversationally, previewed and saved with versions in
the user's data folder. A reusable preference never substitutes for positioning against
the next advertisement.

“Use this mode and rewrite my CV” produces one handoff containing selection and the
generation request. The host imports it, reads the saved brief, generates and reviews
proposals, then publishes their exact version. The static page cannot start the host
agent by itself. It tells the user to copy the request into chat or save it; no second
generation confirmation is required. An equivalent direct chat instruction works too.

Accepted, rejected, edited and alternative requests remain in the same Studio workflow.
Application/source/batch identity and suggestion content identities bind decisions to
the wording reviewed. Assembly refuses a mismatched source or suggestion batch. Each
round has a separate output file and durable source snapshots/history. Final review
checks the assembled content against the decisions as well as the shared objectives.
Desk shows the selected mode and the next writing step from this same record.

## Trace to the agreement

Requirement ids refer to [the agreed brief](rewrite-engine-agreed-brief-2026-09-20.md).
Paths below are relative to `skills/resu-studio`, unless prefixed with `tools`.

| Requirements | Where the behaviour is carried |
|---|---|
| R01, R03 | `SKILL.md`, `references/writing-engine.md`, `assets/writing.js`: one journey, choice plus generation request, then wording decisions. |
| R02, R04–R07 | `writing-engine.md`, `positioning.md`, `assets/writing-modes.json`, `templates/writing-review.json`: simultaneous pillars, ATS content/readability, human engagement and job tailoring. |
| R08 | `writing.py`, `proposal_records.py`: full passage claim maps, existing conflict-free evidence ids, snapshots and explicit semantic review; ids alone do not certify meaning. |
| R09–R12 | `positioning.md`: operational pillar definitions, absence rather than invention, raw impact figures, contribution pattern supported by this candidate's history. |
| R13–R14 | `atomising-sources.md`, `writing-engine.md`, `arithmetic.md`: source relationships, alternatives and conditions, uncertainty, ownership, factual answers and conservative arithmetic. |
| R15 | `voice.md` and `rewriting.md`: pronoun-free proposed CV sentences; the previous first-person exception is removed. Letters and chat retain their own grammar. |
| R16 | Persisted brief/section plan, list-order and section-order proposals, explicit new-section proposals, Studio decisions and assembly. |
| R17–R20 | Reconciled `SKILL.md`, `working-with-the-person.md`, `rewriting.md`, `proposing-changes.md`, `achievements.md` and templates: useful reinforcement, specific purposes, coherent accomplishments, space costs and optional achievement counts. |
| R21–R23 | Built-in mode definitions and `writing.py modes/save-mode/prepare`; separate evidence emphasis and expression fields, private versioned definitions and actual application samples. |
| R24–R25 | Saved mode definition, per-ad brief, revision context and scoped requests. Line revisions, application previews and reusable preferences have distinct scopes. |
| R26 | Writing view shows the original and same two sample anchors for each mode, with source excerpts. Instructions require the short chat comparison too. |
| R27 | Expressive mode plus shared boundaries: persuasive/playful expression remains possible; incompatible literal forms are discussed and translated into an application-readable option. |
| R28–R30 | Main skill and workflow references remove internal-phase permission stops; full-ad tailoring remains distinct from scoring depth; revisions preserve the brief and unaffected decisions. |
| R31 | Draft and assembled-document reviews cover pillars, ATS, human reading, tailoring, integrity, coherence and constraints. `finish` verifies assembled content against the decisions. |
| R32–R33 | Desk reads the writing record; Studio collects one portable handoff. Host execution, temporary files and chat-only fallback are described without claiming background AI execution. |
| R34 | Unique job/data-folder browser storage; versioned sources, briefs, modes, requests and proposal batches; immutable history and source copies; content-based suggestion ids; preserved local drafts and explicit legacy restoration. |
| R35–R36 | Mechanical contracts in `writing.py`, `proposal_records.py`, `check.py`, `assemble.py`; semantic duties in the engine instructions. These are explicitly different assurances. |
| R37–R38 | Generic Studio sections retain projects, languages and other source material, including role/date structure and stable line ids. Additional sections and ordering survive assembly. Default layout is `spine`; full delivered-PDF extraction and visual inspection are required. |
| R39 | Studio, job/Desk and report count the scored rows consistently. Partial evidence is not a full match. Frontmatter-only records retain their legacy fallback. |
| R40 | All runtime assets, scripts, templates and instructions live inside the skill directory. Personal modes and application state live in user data. Runtime remains Python standard library plus the existing browser. |

## Records and boundaries

- `3 Jobs/<id>/writing.json`: current application state.
- `3 Jobs/<id>/.writing/<revision>.json`: prior states, requests and published rounds.
- `3 Jobs/<id>/.writing/sources/`: exact source snapshots.
- `2 My record/writing-modes/`: reusable personal preferences, saved by version.
- Browser storage: unsent direction notes, edits and decisions, isolated by job and data folder.

Changes to cited evidence, the CV or job pack invalidate dependent writing. An unrelated
addition to the shared facts ledger does not invalidate this application. A saved mode
update does not silently change existing applications, which retain their selected
definition. Newly relevant facts still require the host to reconsider the case.

The writing agent performs the semantic work. The scripts cannot establish initiative,
causality, an appropriate warmth level or hiring-manager persuasiveness from a fact id.
They require traceable passages and recorded reviews, and prevent the reviewed version
from being silently substituted. Real prose quality remains a matter for reviewing real
applications; the owner deferred comparative writing testing.

## Verification

`tools/run_all_tests.py`: all eight suites passed, including 210 existing checks and
the six new writing lifecycle/browser tests. The new tests cover authorisation,
idempotent request import, stale ads, affected versus unrelated facts, invalid claim
maps, mode versions, changed-suggestion identity, exact decision application, generic
sections, new sections, section order, partial counts, browser handoff, reload and
same-role/employer application isolation. The new-section browser test also assembles
and rebuilds the Studio to check that the section appears exactly once.

Python syntax, JavaScript syntax, `git diff --check` and the skill-only package inventory
were checked. Browser screenshots were inspected. Test artifacts and development-only
Playwright dependencies remain under ignored `.work`; they are not runtime dependencies.

The generic skill-creator validator rejects the repository's pre-existing top-level
`compatibility` frontmatter field. That existing portability declaration was preserved;
the validator's narrower allowed-key list is not a regression introduced by this build.
No claim is made that this validator passed.
