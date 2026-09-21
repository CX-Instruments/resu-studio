# The application writing engine

Read this when preparing mode samples, responding to a writing request, generating proposals or revising a CV. The same engine owns each operation. The host agent writes the language; `scripts/writing.py` keeps the direction, source versions and requests connected.

## Shared objectives

Pursue all four together: evidenced pillars, accurate and readable ATS content, human engagement, and relevance to this advertisement. Truth, interview defensibility, candidate identity and control govern every mode. Do not average away a failure with a higher score elsewhere. The opening should make the supported fit visible in about ten seconds; experience must withstand a hiring-manager read against the selection criteria.

Read the complete CV and job pack. Capture the exact source wording before interpreting it. Retain the relationships between problem, action, ownership, context and outcome. A requested tone never establishes a fact. Preserve job-requirement alternatives and conditions rather than turning every fragment into an independent capability requirement.

Positioning is reconsidered for every advertisement. A reusable mode contributes preferences; this application's evidence and priorities determine its case. A statement about future direction is a targeting signal, not sector experience.

## Prepare the direction and examples

After the source assessment, run `python3 scripts/writing.py modes`. Read the available definitions. Prepare an application-specific input using `templates/writing-input.json` as its shape, replacing the empty values and placeholders with the actual IDs, evidence and samples.

The brief contains:

- the target and the advertisement's most important requirements;
- one central, defensible case and the source boundaries;
- each pillar, supported with fact ids or explicitly absent;
- the section plan: what each section contributes and which evidence earns space;
- voice and the person's preferences;
- application limits, the existing page and bullet budget, and unresolved questions.

`brief.priorities` is a non-empty array of **requirement ID strings from this job's `asks.md`**, for example `"priorities": ["a1", "a2"]` when those are the actual recorded IDs. Read the IDs from that file; do not substitute requirement descriptions, objects such as `{"id":"a1","facts":["f1"]}`, or candidate fact IDs. Priorities say what matters to the employer, not what the candidate has proved. An important requirement may remain a gap. Evidence mappings use a separate source:

| Field | References |
|---|---|
| `brief.priorities` | Existing job-requirement IDs from this job's `asks.md` |
| Supported `brief.pillars.*.facts` | Supporting candidate fact IDs from `facts.md` |
| `brief.section_plan[].facts`, when supplied | Candidate fact IDs used by that section |
| `samples[].profile.claims[].facts` and `samples[].bullet.claims[].facts` | Candidate fact IDs supporting the exact suggested claim |

Use `positioning.md` for the evidence interpretation and `rewriting.md` for sentence execution. Choose evidence before polishing. A strong existing line can stay. Related clauses forming one accomplishment belong together. A profile can establish a capability that experience proves without repeating the same achievement.

Prepare a profile summary and the same experience bullet for each offered mode, normally all built-ins initially. Quote each original exactly. `line` names the source line; `lines` can name several source profile paragraphs. A missing profile uses `line: "new:profile"` and empty `current`. Samples are provisional, not modifications to the source. Map the full suggested text to evidence using ordered `claims` entries, each with exact `text` and supporting `facts`. The entries, joined with spaces, must reproduce the suggestion. Then assess whether those sources actually support each clause; a valid reference alone proves nothing about meaning.

Do not manufacture evidence to demonstrate differences. If the source does not contain a usable experience example, ask the one material question needed. Otherwise proceed with the strongest available evidence and omit unsupported pillars.

### Make the choice worth making

Modes are writing strategies, not synonym lists. Read each definition's emphasis and behaviour as well as its voice. Use the same source passages and evidence pool across the comparison; the profile may select different relevant facts, while the bullet retains its core action, ownership, qualifications and proof. Choose a bullet with enough real context to reveal different approaches. Do not dilute all modes into the same safe middle voice.

Draft each sample from its strategy rather than paraphrasing the first mode. Credible foregrounds the method or working pattern; Direct foregrounds result or scale with greater compression; Warm brings the evidenced human context forward; Expressive uses an evidenced sequence or distinctive combination with different cadence. These are preferences, not compulsory templates for every line. None permits losing an essential qualifier, turning an aspiration into experience, or claiming an unmeasured benefit.

Before `prepare`, read the versions beside one another with the names hidden. For each pair, identify a substantive change in emphasis, information order, sentence construction or rhythm. Changing "cut" to "reduced" is not enough. Revise near copies. Record a short `difference` on each profile and bullet describing what this actual sample changes; use `why` to explain its application fit. A mode's promised personality is not evidence that the sample delivers it. If a particular passage reasonably stays the same, say so in `difference`; if both samples cannot demonstrate a distinction, offer fewer choices and explain the limit instead of padding the list. The script rejects identical pairs but cannot judge near copies or prose quality.

Check the differences against the source again. For example, fewer shift gaps does not establish reliable coverage, less team stress or permanently fixed problems. An expressive sequence must not silently broaden a metric, its period, or ownership. Retain the uncertainty in raw numbers. All modes still need the four shared objectives together.

Save the input in this job's folder, then run:

```bash
python3 scripts/writing.py prepare --job <job id> --cv "<source CV.md>" --input "<writing-input.json>"
python3 scripts/build_studio.py --job <job id> --cv "<source CV.md>" --scorecard "<scorecard.md>" --asks-md "<asks.md>" --facts "<facts.md>"
```

An agent-authored preparation format error is internal repair work. Correct it using the template and existing records, then continue building the Studio without asking the person to fix JSON or presenting it as a problem with their CV. Do not change the assessment or invent a mapping to make validation pass. Explain and seek input only when a missing fact, unresolved ambiguity or substantive blocker actually requires the person's involvement; if an internal failure cannot be resolved, report that limitation accurately.

Open the Studio at its Writing tab and hand over Resu Desk. Explain the strongest supported pattern, the actual sample differences and the next action briefly in chat. The Writing view shows each original passage once; opening it reveals the mode versions together. The builder offers optional starting mode, emphasis, voice, rhythm, free-text direction and an explicit reusable-mode choice. Do not repeat those choices as a mandatory questionnaire in chat. The source score and writing samples belong to the same application experience.

Scoring depth is separate from writing quality. Read the full ad either way; use relevant, supported responsibilities to inform writing, without presenting unassessed requirements as verified matches. Do not inflate coverage counts to reward a more appealing voice.

## The user chooses and requests generation

The Studio offers "Use this mode and rewrite my CV". Selection and authorisation to generate travel together. The HTML page cannot run the agent, so the user copies the request into chat or saves it. The handoff contains their mode, adjustments and any current review decisions.

Save the entire handoff in the job folder and run:

```bash
python3 scripts/writing.py request --job <job id> --input "<writing-request.json>"
```

`request` already returns the current context. Do not immediately request the same context again; fetch a particular older batch only if it is needed.

Read the returned brief, selected mode, request and source files. A successful rewrite request is permission to generate; do not ask "shall I proceed?" again. It is not acceptance of the resulting wording. Replaying the same request is idempotent. A stale request is refused because its inputs changed: refresh the samples and show the changed basis, preserving earlier decisions.

Check `transition` first. If `reused` is true and `generation_required` is false, the matching saved round has already been restored: rebuild the Studio and report that reuse by mode name. Do not regenerate or republish it. Otherwise continue generation using the previous round and the captured `working_review` as context. Manual wording, explicit keeps and accepted changes stay on the page by default; mode-related alternatives are suggestions. Use the original source for the proposal contract's `Currently`, while considering the effective wording in the saved marks. The Studio displays that effective wording in the comparison with a new suggestion. Approvals on an identical suggestion with the same supporting evidence can carry forward; different wording never inherits an approval.

The job's existing `.writing` history holds mode definitions, samples, full rewrite batches and partial decisions. No folder per mode is needed. `writing.py history --job <job id>` lists compact round summaries; `writing.py context --job <job id> --batch <batch id>` retrieves one earlier round when needed. Normal command output includes the active round and history summaries, not all historical prose. Reuse requires the same CV, guiding brief and mode definition, with unchanged relevant evidence and job pack. After a finished CV, the next request uses that current CV as its source. A deliberate request to generate a fresh alternative in an otherwise unchanged mode may use `force_regenerate: true`; normal switching should reuse matching work.

In the first progress update after a successful import, name the recorded mode: for example, `I'm rewriting your CV using “Direct, warm and flowing”.` Use `selected.name` for rewrites/revisions and `request.mode_name` for a preview's starting mode. For previews, say that you are preparing samples based on that mode; do not imply a full rewrite has begun. State the mode name again when handing over the resulting suggestions. This is acknowledgement, not another approval question. The copied request starts with the human-readable choice, and its JSON includes `mode_name` and `mode_version` alongside the mode ID. The importer verifies those against the prepared snapshot and supplies them for older ID-only handoffs; do not infer the selection from card order or a generic workflow description.

A chat instruction such as "use the warm version and rewrite it" is equally valid. Record a request with the same fields and exact current revision rather than making the person return to the page. The `id` is a fresh unique value; `mode` is a displayed mode id; `action` is `rewrite`, `preview` or `revise`; `source_hash` comes from the current source. This record captures their instruction, not a newly inferred permission.

## Explore and save a personal mode

A `preview` request asks for adjusted examples, not a full rewrite. Use the requested mode as a starting point and interpret the user's adjustments, including any emphasis, voice, rhythm, free-text direction and things to avoid. Their own words refine the broad controls; do not treat an omitted choice as a new constraint. Create a personal definition with `personal-` id, integer `version`, `name`, `impression`, `emphasis`, `voice`, `behaviour` and `boundaries`. Include a short `signature` for the comparison card. The shared engine always takes precedence over mode text. A literal poem or other conflicting request may be explored conversationally, but application samples must retain explicit facts, readable sentences and scanning requirements; explain the closest compatible expression.

To keep an application-only exploratory definition, include it in the preparation input's `custom_modes` list. A further personal-mode request updates the existing personal option by default, retaining its stable ID and assigning a new version when the definition changes. `prepare` reconciles a newly invented personal ID back to that option. Supply the revised definition and its samples, with `preview_mode` pointing to it. Explain: "This updates your custom option; your earlier wording and decisions remain saved." Only use `keep_custom_modes: true` in the request/preparation when the user explicitly wants a separate additional option.

For a recorded preview request with a nonempty `save_as`, `prepare` saves the resulting canonical definition in the private mode library after validation. Use the returned definition's ID and version; do not save a conflicting speculative version before preparation. Without that explicit reusable-preference intent, the changed definition stays in this job. `writing.py save-mode <mode.json>` remains available for a separately authorised library save. Never save CV facts or employer-specific evidence into a reusable mode. Retain approved examples only when they are generic descriptions of the preference or the user's private examples, never in the shipped plugin.

Prepare refreshed samples on the current CV and rebuild the same Studio. Keep the built-in starting mode and other useful choices in the comparison; the revised personal option replaces its former card rather than adding a near-duplicate. Set `preview_mode` to the revised personal mode so the page opens on that result. This highlights a preview; it does not authorise the full rewrite. The user can compare it with other options and then choose "Use this mode and rewrite my CV". A request that the existing modes sound too similar instead calls for a refreshed comparison under those existing definitions, not a new personal preference. Re-run the contrast and evidence checks above.

The previous state is retained in `.writing` history; the browser retains the personal-mode draft through a rebuild. Use the person's feedback, not a questionnaire. `save_as` is sent only when they explicitly choose to save a reusable mode and supply its name; otherwise the exploration stays in this application. A local instruction affects the named line; an application-wide adjustment changes this brief; a saved preference requires that separate intent. Do not silently turn "make this bullet warmer" into a permanent preference.

## Generate and publish proposals

Read the current brief on every generation or revision. Use its evidence and section plan, then draft only useful changes in page order. The source CV is not freely regenerated. `templates/proposals.md` defines the reviewable output. Each changed factual passage has a claim map; each change has a concrete purpose. Requirements are mandatory for a relevance change, not for every clarity or voice improvement.

Carry the selected mode's emphasis, construction and rhythm from the chosen samples into the full document. During the human-engagement and coherence review, compare representative full-CV passages with the selected samples: explain how the chosen direction survived beyond the preview. Keep section purposes distinct and allow a strong source line to stay; do not force every bullet into a signature formula.

For a changed mode, read the previous active round and current decisions rather than starting from a blank document. Redraft only the proposals that need different wording or evidence. To retain unchanged proposals without copying their text through generation, put their UIDs in `reuse_proposals` on the draft review JSON and write only the changed/new proposals to the proposals file. `publish` combines them and validates the full resulting set; do not reuse a proposal and submit another for the same slot. An empty proposals file is allowed when all proposals are explicitly reused. Reused text still needs to fit the chosen mode and the shared objectives in the whole-document review.

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
