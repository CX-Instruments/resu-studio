# The application writing engine

Read this when preparing mode samples, responding to a writing request, generating proposals or revising a CV. The same engine owns each operation. The host agent writes the language; `scripts/writing.py` keeps the direction, source versions and requests connected.

## Shared objectives

Pursue all four together: evidenced pillars, accurate and readable ATS content, human engagement, and relevance to this advertisement. Truth, interview defensibility, candidate identity and control govern every mode. Do not average away a failure with a higher score elsewhere. The opening should make the supported fit visible in about ten seconds; experience must withstand a hiring-manager read against the selection criteria.

Read the complete CV and job pack. Capture the exact source wording before interpreting it. Retain the relationships between problem, action, ownership, context and outcome. A requested tone never establishes a fact. Preserve job-requirement alternatives and conditions rather than turning every fragment into an independent capability requirement.

Positioning is reconsidered for every advertisement. A reusable mode contributes preferences; this application's evidence and priorities determine its case. A statement about future direction is a targeting signal, not sector experience.

## Prepare the direction and examples

After the source assessment, run `python3 scripts/writing.py modes`. Read the available definitions. Prepare an application-specific input using `templates/writing-input.json` as its shape, replacing the empty values with the actual evidence and samples.

The brief contains:

- the target and the advertisement's most important requirements;
- one central, defensible case and the source boundaries;
- each pillar, supported with fact ids or explicitly absent;
- the section plan: what each section contributes and which evidence earns space;
- voice and the person's preferences;
- application limits, the existing page and bullet budget, and unresolved questions.

Use `positioning.md` for the evidence interpretation and `rewriting.md` for sentence execution. Choose evidence before polishing. A strong existing line can stay. Related clauses forming one accomplishment belong together. A profile can establish a capability that experience proves without repeating the same achievement.

Prepare a profile summary and the same experience bullet for each offered mode, normally all built-ins initially. Quote each original exactly. `line` names the source line; `lines` can name several source profile paragraphs. A missing profile uses `line: "new:profile"` and empty `current`. Samples are provisional, not modifications to the source. Map the full suggested text to evidence using ordered `claims` entries, each with exact `text` and supporting `facts`. The entries, joined with spaces, must reproduce the suggestion. Then assess whether those sources actually support each clause; a valid reference alone proves nothing about meaning.

Do not manufacture evidence to demonstrate differences. If the source does not contain a usable experience example, ask the one material question needed. Otherwise proceed with the strongest available evidence and omit unsupported pillars.

Save the input in this job's folder, then run:

```bash
python3 scripts/writing.py prepare --job <job id> --cv "<source CV.md>" --input "<writing-input.json>"
python3 scripts/build_studio.py --job <job id> --cv "<source CV.md>" --scorecard "<scorecard.md>" --asks-md "<asks.md>" --facts "<facts.md>"
```

Open the Studio at its Writing tab and hand over Resu Desk. Explain the strongest supported pattern, the available sample differences and the next action briefly in chat. Do not give the user a second configuration form. The source score and writing samples belong to the same application experience.

Scoring depth is separate from writing quality. Read the full ad either way; use relevant, supported responsibilities to inform writing, without presenting unassessed requirements as verified matches. Do not inflate coverage counts to reward a more appealing voice.

## The user chooses and requests generation

The Studio offers "Use this mode and rewrite my CV". Selection and authorisation to generate travel together. The HTML page cannot run the agent, so the user copies the request into chat or saves it. The handoff contains their mode, adjustments and any current review decisions.

Save the entire handoff in the job folder and run:

```bash
python3 scripts/writing.py request --job <job id> --input "<writing-request.json>"
python3 scripts/writing.py context --job <job id>
```

Read the returned brief, selected mode, request and source files. A successful rewrite request is permission to generate; do not ask "shall I proceed?" again. It is not acceptance of the resulting wording. Replaying the same request is idempotent. A stale request is refused because its inputs changed: refresh the samples and show the changed basis, preserving earlier decisions.

A chat instruction such as "use the warm version and rewrite it" is equally valid. Record a request with the same fields and exact current revision rather than making the person return to the page. The `id` is a fresh unique value; `mode` is a displayed mode id; `action` is `rewrite`, `preview` or `revise`; `source_hash` comes from the current source. This record captures their instruction, not a newly inferred permission.

## Explore and save a personal mode

A `preview` request asks for adjusted examples, not a full rewrite. Use the requested mode as a starting point and interpret the user's adjustments. Create a personal definition with `personal-` id, integer `version`, `name`, `impression`, `emphasis`, `voice`, `behaviour` and `boundaries`. The shared engine always takes precedence over mode text. A literal poem or other conflicting request may be explored conversationally, but application samples must retain explicit facts, readable sentences and scanning requirements; explain the closest compatible expression.

To keep an application-only exploratory definition, include it in the preparation input's `custom_modes` list. When the user explicitly names a reusable preference to save, write the definition in their private folder and run `writing.py save-mode <mode.json>`. Never save CV facts or employer-specific evidence into a reusable mode. Retain approved examples only when they are generic descriptions of the preference or the user's private examples, never in the shipped plugin.

Prepare refreshed samples on the current CV and rebuild the same Studio. The previous state is retained in `.writing` history. Use the person's feedback, not a questionnaire. A local instruction affects the named line; an application-wide adjustment changes this brief; a saved preference requires that separate intent. Do not silently turn "make this bullet warmer" into a permanent preference.

## Generate and publish proposals

Read the current brief on every generation or revision. Use its evidence and section plan, then draft only useful changes in page order. The source CV is not freely regenerated. `templates/proposals.md` defines the reviewable output. Each changed factual passage has a claim map; each change has a concrete purpose. Requirements are mandatory for a relevance change, not for every clarity or voice improvement.

Keep an unchanged line unchanged. Protect useful context and raw numbers. Additions cost space and need an explicit removal or a user-approved higher budget. A move is an `Order` proposal naming the list and original indices. For section ordering, use `Line: document/sections` and `Order` containing every existing heading slug exactly once. For a new section, follow the `Section` contract in `achievements.md`, using `^` for a new profile before the first section. An optional achievement section must earn its space and can draw from one role; never force six lines or a cross-employer claim. A new section is proposed explicitly before its contents are treated as approved.

Before publication, inspect the proposed document as a whole, not just the individual sentences. Complete `templates/writing-review.json` with substantive notes under each objective: pillars, ATS content, human engagement, tailoring, integrity, coherence and constraints. At this stage ATS review covers structure and wording, not a claim that a PDF has been checked. Resolve findings before publication; the script validates completeness, not the quality of your judgement.

```bash
python3 scripts/writing.py publish --job <job id> --proposals "<proposals.md>" --input "<draft-review.json>"
python3 scripts/build_studio.py --job <job id> --cv "<source CV.md>" --scorecard "<scorecard.md>" --asks-md "<asks.md>" --facts "<facts.md>"
```

The Studio loads the published version from the writing record. Editing a loose proposals file does not silently change already-published suggestions. Each suggestion has a content identity, so reusing the display label P1 cannot inherit acceptance of different wording.

## Review and ask for another

The user accepts, rejects, edits or asks for another version in the Studio. Do not require them to tick untouched CV lines. Unreviewed suggestions are not approvals. Preserve unsent decisions before rebuilding. Their direct chat requests are also valid; record them rather than forcing a particular UI route.

For a revision request, save and import the handoff, read its decisions and current brief, and regenerate only what is requested or materially affected. Retain the same full text and evidence map for unaffected proposals so their identities and decisions survive. Keep rejected suggestions in the history and do not repeat them without relevant new evidence or a changed request. Never silently reset manual edits.

If a material factual update invalidates a pending request, prepare a refreshed brief with its affected samples. Carry forward the already-authorised direction when it still fits the user’s instruction; seek a new choice only if the direction itself must change. A factual answer goes to `answers.md` and, when appropriate, `facts.md` before use. Preserve source conflicts. If facts or the advertisement change, reconsider the affected brief and suggestions; do not use stale claims to continue a smoother flow. A request for another writing direction can be fulfilled after current decisions are preserved, with new samples on the effective current CV.

## Assemble, review and finish

Save the Studio's decision file. `assemble.py` validates engine decision identities and source version before applying them. It copies untouched content through and keeps the durable archive. Give each engine assembly round its own output filename, such as `cv-target-r2.md`, so the reviewed source remains intact. A requested alternative must be answered before that proposal is closed; unrelated accepted decisions remain available.

Read the assembled CV against the current brief and source evidence. Check dependencies: for example, rejecting the only proof bullet may leave a profile claim insufficiently demonstrated. Propose a specific repair and preserve the user's choice. Avoid an endless polish loop: finish when the substantive objectives are met, not when every sentence matches a preferred style.

Review the actual rendered document and full PDF extraction, including all sections, role/date association, names, contacts and text completeness. Respect the application's page/word limits. Layout is not allowed to repair overflow by hiding or rewriting content. `ats.md` and `rendering.md` govern this step. Record final findings using the review template, then run:

```bash
python3 scripts/writing.py finish --job <job id> --cv "<assembled CV.md>" --input "<final-review.json>" --decisions "<cv-decisions.json>"
```

Only mark the writing ready when the substantive review and delivered output are complete. `needs_attention` keeps the remaining work visible on the Desk. Rebuild the Studio from the current assembled CV. A later revision uses that current CV and the same application direction, with a new review round.

The optional cover letter or statement uses the same evidence and application positioning, with its own format, pronouns and purpose. Never write an unrequested companion document merely to complete a phase count.

## Ownership and limitations

`writing.json` is this application's current direction; `.writing/<revision>.json` retains prior rounds. Source snapshots live in `.writing/sources` beside that history. Custom reusable modes live under `2 My record/writing-modes`. Built-ins ship under `assets/writing-modes.json`. Source fingerprints identify the precise evidence and CV used. Existing jobs without a writing record remain readable; prepare fresh samples before attributing their wording to a new mode.

The Desk and Studio are views of the same record. The agent runs commands, writes files and rebuilds views; the person should not have to manage JSON or commands. In a host with no execution, perform the same understanding, examples, choice, proposals and revision loop in chat and state that no persistent files or HTML were created.
