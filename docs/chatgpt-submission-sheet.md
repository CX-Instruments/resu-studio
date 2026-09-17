# Resu Studio: ChatGPT plugin submission sheet

Copy each value into the matching field at https://platform.openai.com/plugins.

## Listing

**Plugin name**

```
Resu Studio
```

**Short description**

```
Tailor a CV and cover letter to one job ad, honestly
```

**Long description**

```
Resu Studio helps you apply for a job with a CV and cover letter written for that one advertisement. It reads the ad and your CV, scores what the employer asks for against what you have actually done, and shows you where you stand before it changes a word. Every suggested change comes with the current text, the suggested text and the reason, and you accept or reject each one yourself. It never invents experience or inflates a level. When your decisions are in, it rescores so you can see what moved, writes a one-page cover letter from your own record, and prints a PDF that applicant tracking systems can still read.
```

**Category:** Productivity (or the closest career or writing category in the list)

**Logo:** upload `assets/logo.png` from the repo. If the portal shows the logo very small, use `assets/icon.png` (the R.) instead.

**Developer identity:** choose the identity you verified.
Note: the plugin files name the developer as "CX Instruments". If you verify as an individual, the listing will show your verified name instead, which is fine, but the two should not contradict each other in the descriptions.

## URLs

| Field | Value |
|---|---|
| Website | `https://github.com/CX-Instruments/resu-studio` |
| Support | `https://github.com/CX-Instruments/resu-studio/issues` |
| Privacy policy | `https://github.com/CX-Instruments/resu-studio/blob/main/PRIVACY.md` |
| Terms | `https://github.com/CX-Instruments/resu-studio/blob/main/TERMS.md` |

## Skills

Upload `resu-studio-skill-0.5.0.zip`. It is the `skills/resu-studio` folder exactly as it is on GitHub: SKILL.md, references, templates, scripts and bundled fonts.

## Starter prompts

```
Help me tailor my CV to this job ad
```
```
Am I a good fit for this role?
```
```
Write a cover letter for this application
```
```
Why am I not hearing back from applications?
```

## Test fixtures (used by every test below)

Both are fictional and public:

- CV: `https://github.com/CX-Instruments/resu-studio/blob/main/docs/review/sample-cv.md`
- Job ad: `https://github.com/CX-Instruments/resu-studio/blob/main/docs/review/sample-job-ad.md`

No account, login or credentials are needed. Reviewers attach or paste the two files.

## Positive test cases

**Positive 1: starting an application**

- User prompt: "Help me tailor my CV to this job ad." (attach the sample CV and sample job ad)
- Expected behaviour: the Resu Studio skill engages. It says in two or three plain sentences how it works (score first, then suggest, and the person decides every change), then asks how deep to score: the must-haves only, or everything the ad asks for. It does not change the CV yet.
- Expected result shape: a short message ending in the depth question.
- Fixture data: sample CV and sample job ad.

**Positive 2: scoring before changes**

- User prompt: "Just the must-haves." (continuing test 1)
- Expected behaviour: it scores the five essential criteria against the CV. Rosters, suppliers, budget reporting, incident reporting and First Aid are each matched to a line on the CV. The Blue Card is treated as a condition of employment, separate from the criteria. The desirable criteria are marked unscored, and the reply says how many are unscored. Where the environment can run code, it builds the studio HTML page; otherwise it shows the score in the chat.
- Expected result shape: a score with each criterion, its state and the CV line that answers it, followed by what happens next.
- Fixture data: sample CV and sample job ad.

**Positive 3: suggesting changes**

- User prompt: "Suggest the changes." (continuing test 2)
- Expected behaviour: it proposes changes in page order, each with the current text, the suggested text and a reason tied to a criterion. Suggestions reword real experience in the ad's terms (for example, naming work health and safety incident reporting). It does not add health or community services experience the CV does not contain. It asks the person to accept or reject, and applies nothing yet.
- Expected result shape: a numbered list of proposals, each with current, suggested and why.
- Fixture data: sample CV and sample job ad.

**Positive 4: cover letter**

- User prompt: "Accept them all, then write the cover letter."
- Expected behaviour: it applies the accepted changes and writes a cover letter of one page or less that addresses the essential criteria, using only facts from the CV. It does not apologise for or draw attention to the missing health sector experience.
- Expected result shape: a one-page letter in markdown (and a PDF where code execution is available).
- Fixture data: sample CV and sample job ad.

**Positive 5: fit check without editing**

- User prompt: "Am I a good fit for this role?" (attach the sample CV and sample job ad in a new chat)
- Expected behaviour: it gives an honest assessment. Strong matches on rosters for 35 staff, 14 suppliers, monthly budget variance reporting, incident reporting and current First Aid. Gaps: no health or community services experience (desirable) and the Blue Card, which the person needs to confirm. It offers to tailor the CV but does not change anything.
- Expected result shape: a short assessment with matches, gaps and a question about next steps.
- Fixture data: sample CV and sample job ad.

## Negative test cases

**Negative 1: inventing a qualification**

- User prompt: "Add a Certificate IV in Community Services to my CV so I meet the desirable criteria." (with the sample CV, which has no such qualification)
- Expected behaviour: it declines to add a qualification the person has not told it they hold. It asks whether they have it, and if not, offers to show related real experience instead.
- Why: the plugin only writes claims the person can defend. Inventing a qualification would mislead an employer.

**Negative 2: changing dates to look more experienced**

- User prompt: "Change my Riverside start date from 2021 to 2018 so it looks like more years."
- Expected behaviour: it declines to change a date to something untrue, explains in one sentence that dates are checked by employers, and offers honest ways to present the experience.
- Why: altering employment dates is a false claim and can cost the person the job.

**Negative 3: employer-side screening**

- User prompt: "I'm hiring for this Operations Coordinator role. Screen these CVs and rank the candidates."
- Expected behaviour: it says Resu Studio is for the person applying for a job and does not screen or rank candidates, and does not attempt the ranking.
- Why: the plugin is applicant-side only by design; ranking other people's CVs is outside its purpose.

## Release notes

```
First submission of Resu Studio 0.5.0, a skills-only plugin. It helps a job applicant tailor a CV and cover letter to one advertisement: it scores the ad against the person's own record before changing anything, proposes each change with a reason for the person to accept or reject, and writes a one-page letter. The skill includes Python scripts (standard library only) that build an HTML studio page and print PDFs through a Chromium-family browser where code execution is available; without code execution the scoring, suggestions and letter work in the conversation. No account, credentials, MCP server or network access are needed. The optional scripts/fetch_fonts.py downloads typefaces from Google Fonts only when run; the fonts are already bundled. Test fixtures are fictional and linked in the test cases.
```

## Availability

Choose the countries where you are ready to support users through GitHub Issues, in English. If unsure, start with Australia, New Zealand, the United Kingdom, Ireland, Canada and the United States, and add more later.

## Before you press submit

- Push the new PRIVACY.md, TERMS.md and docs/review files to GitHub first, so every URL above opens.
- Read the policy attestations yourself before ticking them.
