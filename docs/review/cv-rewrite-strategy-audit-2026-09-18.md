# CV rewrite strategy audit

Date: 18 September 2026  
Branch: `review/cv-rewrite-strategy`  
Scope: the rules, templates, scripts, tests and product claims that determine suggested CV rewrites, both for a specific advertisement and for a CV created without one.

## Executive decision

The tailored-CV workflow has a strong ethical core and a useful approval model. It preserves the person's facts, exposes every change, protects page budgets and checks the finished PDF. Those are meaningful differentiators.

It does not currently support a general CV as an end-to-end workflow. A few code paths tolerate missing advertisement data, and the cover-letter guidance mentions a general resume, but the rewrite contract requires every change to answer an advertisement item. The job record, scorecard, proposal schema, Studio copy and checks all assume an advertisement exists.

The recommended product model has three explicit modes:

1. **Application CV:** a named advertisement is available. Match supported evidence to that employer's requirements.
2. **Target-market CV:** no advertisement is available, but the person can name a role family, level, sector, geography and likely submission route. Build a target brief and optimise for it without pretending it is an employer's specification.
3. **Baseline CV:** neither an advertisement nor a useful target is available. Improve accuracy, clarity, evidence, consistency, scanability and parsing only. Do not issue a fit score or claim market relevance.

This distinction should be implemented before adding more rewrite advice. Without it, a general-CV request either has to violate the current rules, invent advertisement-style requirements, or give a much thinner service than the product implies.

This audit also needs a positive writing destination, not only stricter controls. The companion proposal in `docs/review/rewrite-positioning-design-2026-09-18.md` defines the missing positioning and narrative layer: credible conviction, a person-specific positioning brief, evidence pillars, tone controls and whole-document rewriting before individual line edits.

## What is already strong

- Every substantive line must trace to something the person wrote or confirmed.
- The rules prohibit verb promotion, invented figures, silent cuts and unapproved rewrites.
- Existing voice is preserved instead of being normalised into a generic house style.
- The current/suggested/why pattern makes changes inspectable.
- Page and slot budgets prevent uncontrolled expansion.
- Employer terminology is used only where the person's evidence supports it.
- The final PDF is read back as text, which is a practical parsing check.
- The person accepts or rejects each change and rejected changes remain recorded.

These should remain the foundation.

## Findings, in priority order

### P0. General CV creation is not a supported workflow

Evidence in the repository:

- `SKILL.md:317` requires a job to be started from the role and employer in an advertisement.
- `SKILL.md:326` requires the advertisement and job pack to be copied into that job.
- `references/rewriting.md:17` says every change must earn its place against an advertisement.
- `references/proposing-changes.md:211` says a proposal may never have an empty `Answers:` field.
- `references/achievements.md:17` says key achievements are drafted against the advertisement.
- `scripts/jobs.py:724` describes the data model as one folder per job advertisement.
- `scripts/build_studio.py:824` requires a role or a job record.
- `assets/studio.html:499` labels the scoring view “Your CV against the advertisement”.

The only explicit no-advertisement path is for a letter scaffold in `references/assemble-and-print.md:362`. It does not define how the CV itself is selected, rewritten, assessed or stored.

Impact:

- The assistant has no valid basis for deciding relevance or ordering in a general CV.
- `Answers:` and scorecard rows cannot be populated honestly.
- A user can receive inconsistent behaviour depending on which instruction the host follows.
- A “general CV” can accidentally become a generic CV, which is less useful to a recruiter and difficult to tailor later.

Recommendation:

- Add `mode: application | target-market | baseline` to the working record and every generated artefact.
- Add `templates/target-brief.md` for target-market work. Its inputs should be role family, seniority, sector or domain, geography, likely recipient, submission route and any constraints the person names.
- Keep an optional `audience` or `target` record separate from employer asks. Do not present inferred market norms as requirements.
- Allow a baseline CV to be created with no fit score. Label the result as a document-quality review.
- Store target-market and baseline documents separately from job applications, or extend the current record with a real `kind` field. Do not create a fictional employer or advertisement.

### P0. The default design is known to be unsafe for ATS parsing

`references/ats.md:122` says all eight sidebar layouts interleave. `references/ats.md:146` says the default is `sidebar-dark` and that it interleaves. `scripts/render_cv.py:2453` makes that layout the program default. At the same time, `README.md:15` says the text remains readable by an applicant tracking system.

Text being extractable is necessary but not sufficient. The repository's own tests show that extracted sections can arrive in the wrong order, with headings and content interleaved. Greenhouse also lists columned layouts, text boxes, headers, footers and complex formatting as causes of partial or unsuccessful parsing.

Recommendation:

- Make an extraction-safe, single-reading-order layout the default. Based on the repository's current measurements, `spine` is the best initial candidate, subject to regression tests.
- Record the likely destination as `upload`, `email/direct`, `human/referral` or `unknown`.
- Use the parsing-safe layout when the destination is `upload` or `unknown`.
- Let the person choose a more visual layout for a known human route after showing the trade.
- Change the product claim to: “The PDF contains real text and is extraction-tested. Parsing still depends on the receiving system and layout.”
- Validate the whole extracted document, including name, contact details, section order, employer/title/date grouping and missing text. A successful `pdftotext` run alone is not an ATS pass.

### P1. The scoring labels overstate precision

`references/scoring.md:52` includes `none` and `unscored` in the denominator. `references/scoring.md:56` gives a full “you have” count to `near`, even though `near` means only part of an ask is answered. `references/scoring.md:60` says a reader would find only items in `page`, excluding supported synonyms in `buried`.

The two gauges are useful diagnostic counts, but they are not percentages of qualification or predicted success. The current wording can make them look like both.

Recommendation:

- Rename “What a reader would find” to “Visible in the employer's terminology”.
- Report `near` separately, or give it no full point. Do not silently turn a partial match into a whole match.
- Exclude `unscored` from a completion denominator and always show it as outstanding work.
- Report conditions separately from capability coverage.
- Keep any verdict qualitative and show the explicit must-have evidence behind it.
- Do not use this scoring model in target-market or baseline mode.

### P1. The rewrite rules are principled but too absolute in places

The best rules are evidence preservation, honest verbs, voice preservation, no invented figures and no unsupported claims. Several style rules are presented as universal hiring truths without evidence:

- `references/voice.md:27` bans every em dash and en dash because they are described as a machine-writing tell.
- `references/voice.md:43` bans trait terms outright, including `detail-oriented`.
- `references/voice.md:95` requires one claim per bullet and about thirty words.
- `references/rewriting.md` normally prefers outcome-first construction.

Risks:

- A supported employer term can be removed even when an exact keyword search would benefit from it.
- “One claim” can be interpreted so narrowly that an action, its context and its result are split apart.
- Outcome-first wording can become repetitive or unnatural when the action is the differentiator.
- Punctuation preference is being treated as a success factor instead of a house-style choice.

Recommendation:

- Ban unsupported self-labels, not individual words. A trait term may appear when the employer uses it and the same line demonstrates it with evidence.
- Replace “one claim” with “one main message”. A bullet may contain action, context, scale and result when they form one coherent accomplishment.
- Treat thirty words as a review trigger, not a hard success rule.
- Lead with the most decision-relevant element: outcome, action, scope or constraint. Do not prescribe one order for every line.
- Keep punctuation consistent with the person's regional style. If the product retains a no-dash house style, describe it as style, not as an ATS or authenticity rule.
- Preserve exact and approximate figures as the person states them. Exact figures are useful, but false precision is not.

### P1. Hiring-manager engagement needs an explicit selection model

The current rules optimise strongly for advertisement coverage and duplication control. They say less about which evidence is most persuasive when several true facts answer the same requirement.

Add a selection rubric for every line considered for the page:

- relevance to the named role or target
- strength and specificity of evidence
- recency, where recency matters
- scope, complexity and level of responsibility
- outcome or value, when one is known
- distinctiveness compared with the rest of the CV
- interview defensibility
- duplication and page cost

Use the rubric to choose evidence, not to manufacture a numerical “quality score”. The reason shown to the person should remain plain language.

Profiles should be optional. When used, a profile should establish role identity, level or scope, domain and one or two evidence-backed differentiators. It should not be a stack of adjectives or a miniature cover letter.

### P1. The key-achievements rules conflict with the budget rule

`references/achievements.md:46` always drafts six candidate lines, whether the record supports that number or the document needs the section. `references/achievements.md:169` says four achievements cost about a third of a page and that nothing is removed to pay for them. That conflicts with the global rule that every addition requires a removal or an explicitly increased budget.

The requirement that each achievement span more than one employer is also too restrictive. A person's strongest evidence may come from one role, particularly early in a career or after a major change in scope.

Recommendation:

- Make the section optional and evidence-led.
- Draft zero to six candidates, with no padded minimum.
- Permit a single-role achievement when it is exceptional and its context is clear.
- Avoid duplication by choosing whether the claim lives in the summary panel or the role, with the person's approval.
- Charge every selected achievement to the page budget.

### P1. Written policy is not fully enforced by `check.py`

`references/proposing-changes.md` requires `Answers:` and `Draws on:` for additions and rewrites. In `scripts/check.py:289`, ask IDs are checked only if an `Answers:` line exists. The equivalent fact check behaves the same way. Missing or empty fields therefore pass. `check_proposals()` calls the dash check, but it does not run the voice checks on suggested text.

Other documented rules that are not mechanically checked include proposal kind, full-text `Currently:` matching the source line, non-empty traceability by mode, page order, repeated openings, a coherent main message, and budget balance.

Recommendation:

- Parse proposals into a structured record once and validate that record in both `build_studio.py` and `check.py`.
- Require non-empty fact IDs for every addition or rewrite.
- In application mode, require valid ask IDs. In target-market mode, require valid target-brief IDs. In baseline mode, require a valid quality basis such as `clarity`, `accuracy`, `consistency`, `duplication`, `structure` or `parsing`.
- Verify `Currently:` against the exact source line before showing the proposal.
- Run the same content checks on `Suggested:` before it reaches the person.
- Test the proposal order and budget ledger.
- Keep judgement-heavy checks as warnings, not false certainty.

### P2. The proposal contract contradicts its question path

`references/proposing-changes.md:8` says every entry must carry complete current and suggested text. The scripts also support a proposal that contains a question and no suggestion because a missing fact should be asked rather than invented. Both behaviours are sensible, but the schema does not state them consistently.

Recommendation:

- Define two record types explicitly: `change` and `question`.
- A `change` requires `Suggested:`. A `question` requires `Question:` and must not pretend a rewrite already exists.
- When the answer arrives, close the question and generate a new traceable change record.

### P2. The product should optimise leading indicators, not promise hiring success

No wording rule can guarantee interviews. Outcomes also depend on the person's experience, applicant pool, labour market, screening policy, referrals and bias. The plugin can credibly optimise:

- evidence coverage against explicit requirements
- evidence visibility and terminology
- parseable reading order
- scanability and document consistency
- factual and interview defensibility
- user control over changes

If outcome learning is added later, keep it local and optional. Useful measures are application route, interview reached, parsing corrections requested, accepted suggestions and rejected suggestions. Do not turn a small personal history into a universal success model.

## Recommended mode contracts

| Contract | Application CV | Target-market CV | Baseline CV |
|---|---|---|---|
| Required input | CV plus advertisement and referenced pack | CV plus target brief | CV |
| Relevance source | Employer asks | Person-approved target signals | None |
| Rewrite trace | Ask IDs plus fact IDs | Target IDs plus fact IDs | Quality basis plus fact IDs |
| Assessment | Requirement coverage and visibility | Positioning review against target brief | Accuracy, clarity, evidence, consistency, scanability, parsing |
| Score | Diagnostic counts, clearly labelled | No employer-fit percentage | No fit percentage |
| Suggested ordering | Employer priority plus evidence strength | Target priority plus evidence strength | Readability, chronology and evidence strength |
| Final claim | Tailored to this application | Positioned for this target market | Clean baseline ready to tailor |

## Recommended rewrite decision order

For each existing or proposed line:

1. **Truth:** Is every claim supported by the record or a saved answer?
2. **Purpose:** Does it answer an employer ask, support the target brief, or fix a baseline quality problem?
3. **Selection:** Is this the strongest available evidence for that purpose?
4. **Voice:** Does it sound like the person at their normal level of formality?
5. **Specificity:** Does it show action, context, scope or outcome without padding?
6. **Terminology:** Are useful audience terms present where the evidence supports them?
7. **Position:** Is it where a recruiter is likely to see it in the relevant role or section?
8. **Cost:** What leaves, or what budget changes, if this line is added?
9. **Defensibility:** Would the person be comfortable answering a follow-up interview question?

## ATS policy to adopt

Treat ATS work as two separate problems:

1. **Parsing:** Can the system recover the person's name, contact details, headings, employers, titles, dates and content in a sensible order?
2. **Discoverability:** Does the document use supported job terminology a recruiter may search for?

The first is tested through full-document extraction and structural assertions. The second is handled through honest terminology matching. Neither is a universal ATS score.

Never add hidden text, unsupported keywords or a detached keyword block. Include both an acronym and its expanded form when the record supports both and the audience may search either.

## Evidence used for this audit

- Greenhouse documents exact keyword filtering and Boolean resume search. This supports honest use of employer terminology, while also showing that behaviour varies by feature and configuration: <https://support.greenhouse.io/hc/en-us/articles/27104809835291-Talent-Filtering>
- Greenhouse lists columns, tables, headers, footers, text boxes, graphics and unclear sections among common parsing problems: <https://support.greenhouse.io/hc/en-us/articles/200989175-Unsuccessful-resume-parse>
- The UK National Careers Service recommends tailoring to a job and, where no description exists, using occupational profiles to identify the target skills and work. This supports a target brief rather than an untargeted “general” match: <https://nationalcareers.service.gov.uk/careers-advice/cv-sections>
- Yale's writing guidance emphasises the person's own action, project or problem, result, evidence and context. It supports evidence-rich bullets, but not a mandatory outcome or number on every line: <https://ocs.yale.edu/resources/writing-impactful-resume-bullets/>
- NACE's 2026 employer survey reports that employers look for evidence of teamwork, problem solving, communication, technical and analytical skills. These are useful broad signals for an early-career target brief, not a universal checklist for every occupation or level: <https://naceweb.org/docs/default-source/default-document-library/2026/publication/research-report/2026-job-outlook-report-spring-update.pdf>
- A 2023 eye-tracking study of 221 recruiters hiring computer-science graduates found attention to experience and education useful in predicting decisions, and concluded that clear, concise documents deserve emphasis. Its population is limited, so it should inform scanability rather than become a universal timing claim: <https://doi.org/10.3390/make5030038>

## Proposed implementation sequence

### Change set 1: contracts and copy

- Define the three modes in `SKILL.md`.
- Add the target-brief template and mode-aware proposal requirements.
- Revise the absolute style rules.
- Correct the ATS claims and choose the safe default.
- Reconcile the achievements budget and question proposal schema.

### Change set 2: data and validation

- Add `kind` or `mode` to job/work records.
- Support non-application workspaces without fictional advertisements.
- Make proposal validation mode-aware.
- Add structural ATS extraction checks.
- Rename the tailored scoring gauges and correct their counting rules.

### Change set 3: Studio

- Show an application score, target-positioning review or baseline-quality review according to mode.
- Replace advertisement-only copy when no advertisement exists.
- Present the destination and layout trade before PDF generation.
- Keep decisions isolated by stable workspace ID rather than role text.

### Change set 4: tests and evaluation

- Add a complete no-advertisement fixture and end-to-end test.
- Add target-market and baseline proposal validation tests.
- Add adversarial tests for empty traceability, unsupported wording, verb promotion, missing budget cost and source-line drift.
- Add ATS extraction fixtures for name, contacts, headings, job-title/employer/date association and section order.
- Create a small human-reviewed rewrite set covering different occupations, seniority levels and regions. Grade truth, relevance, voice, evidence preservation, scanability and defensibility separately.

## Suggested acceptance criteria

- A user can create a baseline or target-market CV without a fake job, employer, advertisement, asks ledger or scorecard.
- Every suggested change has a valid purpose for its mode and a valid fact trail.
- No general CV receives an employer-fit score.
- The default PDF passes the repository's complete extraction checks.
- The README makes no universal ATS or hiring-success promise.
- Suggestions preserve all material information unless a separate, visible cut is proposed.
- The validator fails missing traceability and source-line drift before the Studio is handed over.
- The key-achievements section is optional, evidence-led and included in the page budget.
- Tailored and general workflows both preserve the person's approval over every change.
