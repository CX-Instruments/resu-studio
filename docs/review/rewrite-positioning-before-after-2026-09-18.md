# Rewrite positioning: before, after and test

Date: 18 September 2026  
Status: illustrative acceptance fixture

This fixture uses the fictional Alex Morgan CV and Northside Community Health job
advertisement in this folder. It tests the effect of the positioning layer, not just
whether individual sentences sound smoother.

The source CV is already fairly strong, so the expected improvement is deliberately
subtle. The new version should become more coherent and relevant, not more dramatic.

## What should change

### Likely result from line-by-line rewriting

> Events and operations coordinator with eight years in hospitality and venue
> management, moving into community services operations. Experienced in rostering,
> supplier management, budget tracking and incident reporting.

- Coordinated weekly rosters for 35 casual staff using Deputy, reducing last-minute
  shift gaps from about six a month to one.
- Managed relationships with 14 catering, audio visual and cleaning suppliers.
- Monitored event budgets in Excel and reported monthly variances.
- Developed an incident reporting procedure after two near misses and trained staff.

This is accurate and readable, but it behaves like a checklist. The profile names
capabilities without making the candidate's useful pattern clear. The bullets improve
individually, but the document does not quite explain what connects them.

### Positioning brief before the new rewrite

- **Target:** operational coordination in a six-site community health service.
- **Strongest case:** keeps busy, people-dependent operations reliable, then improves
  the process behind recurring problems.
- **Proof:** a 35-person roster; shift gaps reduced from about six a month to one; 14
  suppliers; monthly budget variance reporting; an incident procedure created after
  two near misses and taught to all staff.
- **Supported employer language:** workforce rostering, supplier contracts, budget
  monitoring, variance reporting and incident reporting.
- **Boundary:** no health-sector experience, supplier service-level responsibility or
  Blue Card status is established. Do not imply any of them.
- **Voice:** plain, operational and assured. No praise words or career-change pitch.
- **Open question:** what draws Alex to community health operations? Use the answer in
  the CV or letter only if Alex wants it stated.

### Expected result with positioning

> **Profile**
>
> Operations coordinator with eight years' experience keeping high-volume,
> people-dependent services running across workforce scheduling, suppliers, budgets
> and incident processes. Combines day-to-day coordination with process improvement,
> using documented procedures and operational information to make delivery more
> reliable.

> **Key skills**
>
> Workforce rostering (Advanced); Supplier management (Advanced); Budget monitoring
> and variance reporting (Intermediate)
>
> Microsoft Excel (Advanced); Deputy (Advanced); Xero (Working knowledge)

> **Venue Operations Coordinator, Riverside Function Centre | 2021 to 2026**
>
> Coordinated daily operations for a 400-guest venue delivering around 180 events a
> year, with responsibility spanning a 35-person casual workforce, 14 suppliers,
> budget tracking and incident processes.
>
> - Built weekly rosters in Deputy and reduced last-minute shift gaps from about six
>   a month to one.
> - Managed supplier relationships across catering, audio visual and cleaning
>   contracts.
> - Monitored event budgets against actual spend in Excel and reported monthly
>   variances to the venue manager.
> - Created the venue's incident reporting procedure following two near misses and
>   trained all staff in its use.

The difference is not louder language. The profile now gives the reader a supported
reason to remember Alex: reliable operations plus process improvement. The role
summary establishes scale once, leaving each bullet to prove a distinct part of the
case. Relevant search terms are present where the evidence supports them. The version
does not pretend that venue work is health experience or upgrade supplier
relationships into service-level ownership.

This is an expected direction, not a mandatory golden answer. A different draft can
pass if it makes the same evidence-led case in Alex's voice.

## How to run a fair A/B test

Use the same CV, advertisement, model and user prompt in two fresh conversations:

1. **A, baseline:** run the released plugin without `positioning.md`.
2. **B, candidate:** run this branch with `positioning.md` active.
3. Stop both runs after the complete set of rewrite proposals. Do not accept changes
   during one run and not the other.
4. Repeat each condition three to five times if model settings are not deterministic.
5. Remove the condition labels and have a reviewer score the outputs blind.

Suggested test prompt:

> Tailor this CV to this job ad. Keep it truthful and concise. I want to sound like
> myself, not salesy. Show me the proposed rewrites but do not apply them yet.

## Scorecard

Score each item from 0 to 2: 0 fails, 1 partly succeeds, 2 clearly succeeds.

| Test | What success looks like |
|---|---|
| Truth and defensibility | Every claim is traceable and could be explained in an interview. This must score 2. |
| Central case | A reviewer can state Alex's useful professional pattern in one sentence. |
| Evidence selection | The strongest relevant facts receive space and weaker facts do not crowd them out. |
| First-page clarity | Identity, operating context, strengths and proof become clear quickly. |
| Contribution | Each bullet distinguishes what Alex did from general team activity. |
| Context and impact | Results, scale, difficulty or responsibility make the work meaningful. |
| ATS relevance | Supported job terms appear naturally in searchable text. |
| Human voice | The wording is direct and believable, without slogans, praise or copied-ad tone. |
| Coherence | Profile, skills and experience reinforce one case without needless repetition. |
| Restraint | Gaps remain honest; ordinary duties are not inflated into achievements. |

The candidate version should beat the baseline on central case, evidence selection,
first-page clarity and coherence without losing any points on truth, human voice or
restraint. A higher keyword count alone is not a win.

## Fast hiring-manager check

Give each anonymised version 20 seconds, then ask the reviewer:

1. What kind of operator is this person?
2. What are they demonstrably good at?
3. Which fact makes that believable?
4. What remains unproved or needs clarification?

The positioning change is working when the first three answers are faster and more
consistent, while the fourth still identifies the genuine health-sector,
service-level and Blue Card gaps.
