# Agreed rewrite engine direction

Date: 20 September 2026  
Repository: `D:\resu-plugin` only  
Branch: `review/cv-rewrite-strategy`  
Status: build authorised by the owner on 20 September 2026; implemented on this branch, with regression verification recorded in `rewrite-engine-build-2026-09-20.md`.

## Purpose and authority

This records the owner's agreement in the design conversation on 20 September 2026. Read it before planning or implementing the rewrite engine. Carry the complete agreement forward, rather than implementing only the latest feature mentioned in chat.

The owner approved the integrated journey, the four simultaneous objectives, the supporting evidence and user-control principles, and the repository-wide dependencies below. They particularly reaffirmed:

> Positioning must be reconsidered against each advertisement.

> The user can explore without committing, then choose "Use this mode and rewrite my CV." That records their direction and requests generation together. We should not follow it with another "shall I proceed?"

At the time it was recorded, this file captured design agreement only. The subsequent instruction “we’re ready for the build” authorised implementation in this repository and branch. Deployment, installation, release and comparative writing evaluation remain outside this build. The owner explicitly kept this work in exploration and put comparative testing aside to focus on getting the engine right. Further user instructions can change that scope.

Existing modifications in `SKILL.md`, `references/rewriting.md`, and the earlier review documents predate this agreement record. Preserve them while reconciling the final design. Do not treat existing code, old reviews, or old branch-specific restrictions as if they already implement this agreement.

## Product centre

**R01. Rewriting is the core experience of the plugin.** Mode exploration, the guiding brief, full rewrite suggestions, approval, requests for another version and assembly form one continuous application workflow. They must not become a separate utility bolted onto the Desk or Studio.

**R02. Quality applies across preferences.** A chosen mode changes evidence emphasis and expression. Every mode still pursues the shared objectives below. A user should not need an "ATS mode" to get readable output or a "warm mode" to avoid lifeless prose.

**R03. Meaningful choices, minimal interruption.** Let the user explore before committing. Combine selection and the request to generate into one deliberate action. Once that request reaches the agent, proceed without asking permission for the same generation again. Selecting a mode does not approve the resulting wording.

## Four simultaneous objectives

These are shared objectives throughout the engine, not competing product modes or a single weighted score that can hide failure in one area.

| ID | Objective | Required behaviour |
|---|---|---|
| R04 | Four evidenced pillars | Surface supported passion, strengths, proof of impact and a distinctive contribution pattern. Omit unsupported pillars. Never manufacture one to complete a framework. |
| R05 | ATS success | Preserve readable structure and extractable content; use supported employer terminology naturally. Treat extraction, terminology and requirement coverage as distinct concerns. Validate the actual final output. Do not claim universal parser compatibility or predicted hiring success. |
| R06 | Human engagement and warmth | Make the contribution concrete, understandable, memorable and recognisable to the person. Preserve context, judgement, beneficiaries and collaboration where supported. Avoid flattening the CV into duty statements. |
| R07 | Tailoring to the specific ad | Use the employer's priorities to guide evidence selection, order and emphasis. Preserve the actual professional identity and boundaries of the person's experience. Reconsider positioning for each advertisement. |

The opening should make the supported fit visible in about ten seconds. Experience should reward a deeper hiring-manager read with evidence against the requirements. Every sentence need not carry all four objectives; the document must deliver them together.

## Evidence and four-pillar interpretation

**R08. Every factual clause must be interview-defensible.** Map it to source CV evidence or a recorded factual answer from the person. Preserve attribution, contribution, dates, qualifications, uncertainty, conditions and scale. A fact reference being present is not proof that it supports the wording. Review implied causality, ownership and seniority as well as explicit claims.

**R09. Passion means evidenced choices and initiative.** Look for repeated work the person chooses and supported examples of going beyond the immediate task: creating procedures, training others or repairing recurring problems. A duty alone does not prove initiative. A stated future direction is a targeting signal, not experience or established motivation in that sector. Do not print "passionate about" as a substitute for evidence.

Express a supported working habit in the profile and through experience. Profile sentence three is a default placement, not a requirement to invent a habit or force a third sentence.

**R10. Strengths are capabilities the target needs and the history demonstrates.** Link each to experience. Use the employer's language where it describes the same work. Distinguish a demonstrated capability from a repeated signature pattern. Skills provide a searchable index; strong bullets supply the proof.

**R11. Impact includes results, scale and artefacts.** Retain raw before/after figures, volume, frequency, team size, scope, dates and documented outputs where present. Never invent a metric or force an outcome. Preserve approximations such as "about". Do not replace raw figures with a derived percentage or imply precision beyond the source. Place proof close to the action and establish role scale where useful without repeating it unnecessarily.

**R12. UVP is an evidenced contribution pattern.** Establish it in the profile, prove it in a strong bullet and reinforce it through different evidence. Never print a "Unique value proposition" heading or a slogan. Differentiation is the aim; the person's CV cannot establish what every other applicant offers.

The fictional fixture's pattern is improving the process behind a problem, documenting it and training others. That is fixture-specific. Do not impose it on other people. Creating a procedure does not alone prove self-initiation; training colleagues does not alone prove subsequent independent operation.

**R13. Preserve relationships during ingestion.** Atomised facts retain their role and source context and the relationships between action, problem, method and result. Preserve compound job-requirement logic, including alternatives such as "X or Y", rather than treating every fragment as independent. Capture the job pack, submission requirements, limits and eligibility information without inventing missing requirements.

**R14. Distinguish evidence, interpretation, preference and uncertainty.** A desired tone is not a fact. A plausible pattern is not automatically a confirmed personal motivation. Ask only useful, material questions after consulting saved answers; otherwise omit unsupported content and continue. Conflicting source facts need resolution before dependent claims are used.

## Writing and document construction

**R15. Language rules support the engine.** The agreed sentence principles are specific, active, clear, fact-based, scannable, "express rather than impress", and no pronouns on the CV. These are not the positioning engine. Reconcile the existing first-person-preservation exception throughout instructions and templates. CV pronoun rules do not automatically apply to chat or cover letters.

**R16. Plan the document before polishing lines.** Establish the central case, select evidence, decide ordering and give each section a job. Profile establishes the case; skills make capabilities easy to find; experience proves it; education and credentials supply relevant qualifications. Additions, moves, removals and structural changes remain reviewable decisions.

**R17. Allow supported reinforcement.** A profile may summarise a capability that experience proves. Distinguish that from repeating the same achievement or metric. Replace conflicting blanket interpretations of "a claim prints once".

**R18. Every change needs a useful purpose.** Valid purposes include relevance, evidence visibility, comprehension, differentiation, voice and economy. A clearer or warmer line can be worthwhile without answering an additional criterion or increasing a match count. Leave strong existing wording alone when no useful change is warranted.

**R19. Preserve useful detail when shortening.** Scale, constraints, standards, beneficiaries, stakeholders and attribution are content. Make substantive removal explicit. Page and section budgets matter; do not silently cut evidence to fit a layout. A bullet should carry one coherent main message, allowing connected action, context and result.

**R20. Structure follows evidence and need.** Profiles and achievement sections must not force unsupported content. Reconcile the fixed six-achievement instruction, cross-employer-only rule and inconsistent budget treatment. Avoid one mandatory bullet rhythm, lead element or career pattern for every person.

## Writing modes and guiding brief

**R21. Default and extensibility.** Use the branch's proposed "credible conviction" direction as the default mode, refined to meet this agreement. Support other modes and conversational creation of personal ones. Legacy behaviour was discussed for comparison, but comparative testing is now deferred; it is not a required shipping mode.

**R22. Separate positioning and expression internally.** The user can see one Writing mode concept. Internally distinguish which evidence leads and what the reader should remember from formality, directness, warmth, rhythm and vocabulary. "Keep this emphasis but make it warmer" should not change facts or arbitrarily rebuild the case.

**R23. Each mode has a guiding definition.** Capture intended impression, evidence emphasis, voice, writing behaviour, boundaries and examples approved as representing the preference. Help the person discover these through samples and reactions. Do not require them to fill in a technical configuration table.

**R24. Three connected scopes persist.**

| Scope | Contents | Lifetime |
|---|---|---|
| Reusable preference | Mode definition, style and positioning approach, boundaries, suitable examples | Can be reused across applications; user-owned custom modes survive plugin updates |
| Application direction | Employer priorities, supported pillars and evidence, central case, section plan, constraints, selected mode version | Specific to this advertisement and source evidence |
| Revision context | Current document and suggestion versions, decisions, rejected alternatives, new facts and requested adjustments | Persists through the review loop and later resumption |

Keep reusable preferences separate from candidate facts and employer-specific claims. Do not copy personal facts into a distributable mode. Adapt an existing preference to each job rather than carrying the previous job's positioning forward unchanged.

**R25. Feedback has a scope.** "Make this bullet warmer" changes that bullet. "Make the whole CV warmer" changes this application's direction. Saving that as a reusable personal mode is a distinct choice. Do not silently generalise a local edit into a global preference.

**R26. Samples precede full rewrite proposals.** After understanding and assessing the CV and ad, show the original text and mode-specific samples of the person's profile summary and the same experience bullet. Explain each emphasis briefly and make supporting evidence inspectable. Provide HTML and a concise chat account where the host can create files; retain the same conceptual flow in chat where it cannot.

Preview samples are provisional suggestions; they do not change the source CV. Clarify that distinction in the "score before rewriting" rules. Preserve earlier samples for meaningful comparison instead of regenerating them whenever a user toggles modes.

**R27. Creative freedom has explicit boundaries.** Users may request persuasive, playful or more expressive writing. Facts and shared application objectives remain binding. The exact handling of a request such as literal poetry, when it conflicts with the agreed sentence and scanning rules, remains a design detail to specify. Do not silently disable requirements or invent claims to satisfy a style request.

## Integrated user journey

1. Capture and faithfully read the CV variants, specific advertisement and relevant job pack. Reuse the person's existing record and answers appropriately.
2. Extract facts and requirements with context and relationships intact; assess the match and constraints.
3. Show the assessment, supported contribution pattern and writing-mode samples as the first meaningful writing choice. Missing pillars do not force a questionnaire.
4. Let the person choose, explore or refine a guiding brief without applying the samples to their CV.
5. "Use this mode and rewrite my CV" records direction and requests generation together. No duplicate confirmation after the request arrives.
6. Generate a coherent set of proposals using the application brief. Show changes in the CV context, with current wording, suggested wording and reasons.
7. Let the person accept, reject, edit or request another version. Preserve unrelated decisions and use the same evidence and brief throughout revisions.
8. Assemble the accepted changes, then review the actual document against all four objectives, factual support, limits and voice. Propose specific repairs where necessary without reversing user choices.
9. Produce the approved finished CV, keeping preview, markdown and delivered output consistent. Related documents, when requested, use the same application understanding with document-appropriate language rules.

**R28. Replace unnecessary stops with meaningful decision points.** Reconcile the repeated seven-phase stop instructions across the skill and references. Continue authorised work. Keep necessary factual clarification, mode/request choices and wording approval visible. The user should not need to understand internal phases.

**R29. Scoring depth must not silently determine writing quality.** The full advertisement is read under the existing contract even when only essentials are scored. Specify how the full ad informs tailoring without claiming that unassessed requirements have been checked or silently expanding a separately agreed assessment scope.

**R30. Review is a continuous loop.** A request for another version is handled within this application, using the active brief and the user's feedback. It does not restart ingestion, erase approvals, repeat answered questions or reintroduce an explicitly rejected suggestion without a relevant new reason.

**R31. Reassess after decisions.** If rejecting a bullet removes the only printed proof for a profile claim, detect the dependency and propose a repair. Factual changes trigger reconsideration of affected suggestions and variants; a tailoring preference does not automatically propagate to other applications. Preserve the user's decisions and distinguish unreviewed, rejected and accepted wording.

## Desk, Studio and handoff

**R32. One state, complementary surfaces.**

| Surface | Role |
|---|---|
| Resu Desk | Application overview with selected mode, writing progress and the next action: choose mode, review changes, continue revisions or open the finished CV |
| Application Studio | Detailed mode samples, guiding-brief refinement, rewrite request, proposal review and current CV preview |
| Chat | Brief explanation, conversational discovery and adjustments, missing facts and receipt of page requests |

Writing must have a prominent place in Studio navigation. A small selector among cosmetic controls does not meet the product direction. Avoid two independent selectors or competing records in Desk and Studio. The exact layout and whether Desk embeds any sample preview remain implementation design details.

**R33. Respect the current transport.** Desk and Studio are generated HTML files with browser-local state. They do not currently invoke a model or write application records directly. The host agent performs generation; Python scripts handle records, page building, checks, assembly and rendering.

In the current architecture, mode selection, adjustments and the rewrite request travel in one handoff. The agent proceeds once it receives that request. A literal browser click that starts generation without a handoff requires a new host connection and must not be implied to exist. The exact affordance should make the real action clear without exposing commands or JSON as the user's job.

**R34. Persist and resume accurately.** Record application identity, source version, brief and mode versions, proposal identity and exact reviewed content. Keep earlier alternatives and decisions. Bind approval to the wording reviewed. Protect unsent browser decisions during rebuilds. Distinguish repeated applications to the same role/employer and keep mode variants from sharing the wrong state.

## Enforcement and delivery

**R35. Separate mechanical checks from judgement.** Code can check required records, source and version identities, reference existence, exact current text and correct application of decisions. Semantic review must assess whether evidence supports each clause, whether the case is coherent and whether the writing is engaging. A reference ID or successful script exit cannot certify those qualities.

**R36. Review at the relevant points.** Apply the shared objectives while forming positioning, making previews, generating proposals, answering rewrite requests and reviewing the assembled result. Do not save all quality judgement for an end-stage score.

**R37. Preserve evidence through every representation.** Source conversion, Studio section handling, proposal placement, assembly, rendering and PDF extraction must agree. Content such as projects or volunteering cannot disappear because a UI schema recognises fewer sections than the renderer. Page limits and reading order remain part of the application outcome.

**R38. Delivery retains the agreed content.** Preserve original sources and durable change history. Render the approved document, without rewriting from the facts ledger during export. Typography or layout changes must not silently alter wording. Validate the actual final output; documented historical layout results are not verification of the current file.

**R39. Keep fit assessment honest and consistent.** Requirement coverage and terminology counts are diagnostics, not a universal writing-quality score. Do not pretend every useful rewrite increases those counts. Reconcile the Studio, Desk and report's differing count sources so their descriptions do not disagree.

**R40. Preserve portability and private ownership.** Built-in rules and mode definitions must be included when only the skill directory is installed. Personal modes, briefs, samples, answers and decisions belong with user data and survive updates. Account for local, temporary hosted and chat-only operation. Do not introduce a hosted service or new dependency as an incidental consequence of a UI selector.

## Repository integration map

These are integration areas, not a final list of patches. Review the actual code before modifying it.

| Area | Existing files | Requirements it must carry |
|---|---|---|
| Entry point and workflow | `skills/resu-studio/SKILL.md`; `references/working-with-the-person.md`, `sources.md`, `studio.md` | R01-R03, R26, R28-R33; opening promise, phase boundaries, mode choice and generation request |
| Source and job understanding | `references/atomising-sources.md`, `scoring.md`, `arithmetic.md`; facts, answers, asks and scorecard templates | R04-R14, R29, R39; context, requirement logic, factual precision and limits |
| Writing policy | `references/positioning.md`, `voice.md`, `rewriting.md`, `proposing-changes.md`, `achievements.md`; CV, proposal and achievement templates | R04-R27, R30-R31, R35-R36; shared engine, modes, planning and justified changes |
| Private records and lifecycle | `scripts/paths.py`, `jobs.py`, `documents.py`; `templates/job.json` | R21-R25, R28-R34, R38-R40; ownership, versions, current progress and resumability |
| Desk | `scripts/build_desk.py`; `assets/desk.html` | R01, R28, R32-R34, R39; application overview and correct next action |
| Studio and handoff | `scripts/build_studio.py`; `assets/studio.html`, `markup.js`; `references/marking.md` | R23-R27, R30-R37; samples, writing navigation, revisions, identity and preserved decisions |
| Checks and assembly | `scripts/check.py`, `assemble.py`; `references/assembling.md`, `assemble-and-print.md` | R08, R17-R20, R31, R34-R38; mechanical guarantees, decision application and whole-document review |
| Rendering and related documents | `scripts/render_cv.py`, `to_pdf.py`, `render_report.py`; `assets/paginate.js`, skins and font assets; `references/rendering.md`, `ats.md`, `cover-letter.md` | R05-R07, R15, R19, R31, R37-R39; content fidelity, readability, limits and application consistency |
| Distribution and product explanations | Manifests, `tools/build_plugin.py`, `tools/sync_version.py`, README and installation/privacy documentation | R01-R03, R32-R33, R40; shipped resources and accurate description of the integrated workflow |

## Findings that must inform implementation

These were found by reading the repository. They are not claims of runtime reproduction.

- The active positioning file supplies an instruction, but the runtime templates and records do not define a persistent guiding brief or writing-mode lifecycle.
- The Studio defaults to Skin and exposes Skin, Skills, Sections and Score as its main tabs. Writing has no equivalent persistent home.
- `job.json` carries broad application stages, scores and notes. It does not identify mode selection, brief revision or a pending rewrite request. Decide how writing progress fits without confusing application status with writing status.
- `build_desk.py` reads job records and the document ledger; the Desk imports changes through `jobs.py apply-desk`. Extend that established relationship coherently.
- Studio storage is derived from role and employer rather than the unique job ID. Proposal decisions use proposal IDs; its CV fingerprint deliberately excludes proposals. Mode variants and repeated applications need stronger identity handling.
- Accepted wording is stored in line edits as well as proposal decisions. The observed concern is stale attribution when IDs are reused; automatic application of changed proposal wording was not demonstrated.
- Exported decisions contain more context than the assembler consumes. A richer handoff must have explicit consumers; adding fields alone does not implement behaviour.
- `build_studio.py` supports a narrower set of sections than the renderer and reports unhandled content. Faithful ingestion and review need a coherent answer for that mismatch.
- Proposal instructions reject changes with no ad ask. This conflicts with useful improvements to clarity, voice and engagement.
- `check.py` checks supplied fact and ask IDs, but does not establish clause-level semantic support. Missing fields and other proposal-contract gaps need deliberate treatment.
- First-person preservation, blanket duplication rules, fixed achievement counts, cross-employer-only achievements and some budget instructions conflict with the agreed flexibility.
- Arithmetic instructions currently treat qualifying career span as experience duration and change some estimates' forms. Reconcile those instructions with precise, defensible claims rather than trusting them because they are existing policy.
- The score displays do not all use the same source for counts. Existing labels also conflate terminology visibility with what a human understands.
- The ATS reference documents historical extraction failures and permits some after disclosure. That policy needs reconciliation with simultaneous human and machine readability; it is not sufficient to report that PDF text is selectable.
- Older handoff documents contain constraints scoped to previous branches, including leaving Studio unchanged. They are historical context, not a reason to omit the newly agreed Studio integration.
- The older audit proposes application, target-market and baseline contexts. Those are different from writing styles. Do not accidentally expand this specific-ad implementation into all those workflows or reuse one ambiguous `mode` field for both concepts.

## Details still to specify, without reopening the agreement

- Exact saved schemas, filenames, source snapshots, stable identifiers and migration behaviour.
- The minimal canonical brief the agent must load for each operation, and how that context is kept complete without unnecessary repetition.
- Studio layout, Desk next-action links and writing-progress representation.
- The precise handoff experience, including how a custom-mode preview request differs from the full rewrite request.
- Handling literal poetry or other preferences that conflict with application-language constraints.
- How to represent document-level plans and linked changes in a per-line review interface.
- How scoring scope, full-ad tailoring and separately identified unassessed requirements interact.
- How a changed source, job ad, mode or brief invalidates dependent suggestions while preserving user decisions and previous versions.
- How existing applications open without a recorded mode, without retroactively claiming their wording came from the new default.
- How whole-document repair proposals remain useful and bounded rather than causing an endless approval loop.

These are design tasks for implementation planning. Do not repeatedly ask the owner to reconfirm principles already agreed here.

## Earlier material

- [Initial strategy audit](cv-rewrite-strategy-audit-2026-09-18.md)
- [Initial positioning design](rewrite-positioning-design-2026-09-18.md)
- [Illustrative before/after fixture](rewrite-positioning-before-after-2026-09-18.md)
- [Correction to the earlier comparison method](rewrite-positioning-test-method-correction-2026-09-18.md)
- [Current proposed positioning instruction](../../skills/resu-studio/references/positioning.md)

Use these as supporting history. This agreement records the subsequent integrated direction. Comparative testing remains deferred; the existence of the earlier testing documents is not an instruction to resume it now.
