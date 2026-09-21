# Rewrite positioning and voice design

Date: 18 September 2026  
Status: discussion proposal, no production rules changed

## The missing capability

Resu Studio currently has strong rules for truth, traceability, matching and user control. It can identify a weak line and improve it. What it does not yet do is form a view of the person before it starts rewriting those lines.

That missing view is not a personal-brand slogan. It is an evidence-led account of:

- the work this person is strongest at
- the problems people rely on them to solve
- how they tend to solve them
- the scale, difficulty or conditions in which they have done it
- who benefits from their work
- what changed because of it
- which parts of that pattern matter to the next employer
- what kind of work they want to keep doing

Without this layer, every bullet can improve while the CV remains a collection of facts. With it, the whole document makes one coherent case.

## The voice target

The finished CV should sound like a capable person describing their work with quiet confidence.

It should be:

- **assured:** it states what happened without hedging or self-congratulation
- **specific:** it names the work, context, scale, difficulty or result that makes the claim meaningful
- **selective:** it includes the evidence that supports the central case and leaves weaker material in the person's record
- **human:** it uses words the person could comfortably say in an interview
- **distinctive through detail:** it is recognisable because of what this person actually did, not because of unusual adjectives or theatrical verbs
- **relevant:** it makes the employer's priorities easy to see where the evidence supports them
- **restrained:** it does not oversell, praise the person, announce a brand or turn every duty into a triumph

The useful shorthand is **credible conviction**.

The reader should finish with a clear sense of what this person is good at and why, without ever being told that they are exceptional, passionate, visionary or uniquely qualified.

## What passion, strengths and value mean here

### Passion becomes a motivation thread

Do not print “passionate about”. Find what the record and the person show:

- work they repeatedly chose or volunteered for
- problems they kept returning to across roles
- responsibilities they sought beyond the minimum
- subjects they continued learning
- outcomes they are proud of and why
- work they want more of in the next role

This becomes a quiet thread through the selection and ordering of evidence. It normally belongs in the profile or cover letter only when the person has said it directly. Elsewhere it is shown by the work selected.

### Strengths become repeated, proved patterns

A strength is not an adjective. It is a pattern of effective contribution seen more than once.

For each possible strength, identify:

- the action pattern
- at least two examples where available
- the conditions in which it worked
- the people or systems affected
- the outcome, standard or recognition that makes it credible

A strength with one example may still be important, but it is a demonstrated capability rather than a signature pattern.

### Unique value becomes differentiated contribution

“Unique” is usually too strong and encourages invented distinction. The useful question is:

> What combination of experience, judgement and way of working makes this person particularly useful for this target work?

The answer should be a compact internal statement, not a slogan printed on the CV. It combines:

- the problems they can take on
- the capabilities they bring together
- the level or context in which they have used them
- the benefit their work creates
- the proof anchors that support the statement

The CV expresses this through its profile, evidence order and selected achievements. It does not label it “value proposition”.

### Impact becomes proof in context

Impact is broader than a number. Valid proof includes:

- a measured change
- time, cost, risk or effort avoided
- something created, repaired or made reliable
- a decision improved
- a standard met under difficult conditions
- scale handled successfully
- people enabled or developed
- trust, responsibility or recognition earned
- an important service delivered consistently

Not every role produces a clean metric. The plugin should never invent one or make an ordinary duty sound transformative. Where no result is known, the proof may be the difficulty, scale, standard, judgement or responsibility involved.

## The positioning brief

Before proposing line edits, the plugin should write a private working brief from the CV, other supplied material and the person's saved answers.

```yaml
professional_identity: "What kind of practitioner or leader the evidence shows"
target: "The role, role family or audience this version serves"
level: "The level of responsibility the evidence supports"
motivation_thread:
  - "Work the person repeatedly chooses or wants more of"
signature_strengths:
  - strength: "A repeated way this person contributes"
    proof: [fact-id, fact-id]
value_pattern: "The useful combination of problems, capabilities and benefit"
proof_anchors:
  - fact-id
  - fact-id
  - fact-id
employer_priorities:
  - ask-id
tone:
  formality: "plain | professional | formal"
  directness: "measured | direct"
  technical_density: "light | field-native | specialist"
  established_voice: "How this person already writes"
do_not_overstate:
  - "Boundaries the evidence does not support"
open_questions:
  - "Only questions whose answers would materially improve the positioning"
```

For an application CV, `employer_priorities` comes from the advertisement. For a target-market CV, it comes from the person-approved target brief. For a baseline CV, it stays empty and the positioning remains descriptive rather than claiming market fit.

The person should see the substance in plain language before rewrites begin:

- what the plugin thinks their strongest professional pattern is
- the three or four facts it is relying on
- what it is still unsure about

They can correct it before that interpretation reshapes the whole CV.

## Discovery before rewriting

The existing workflow extracts facts but does not sufficiently discover meaning. When the source material does not reveal the positioning, ask a small number of high-value questions.

Useful question areas are:

- the work people repeatedly come to them for
- the difficult problem they make easier
- the result they are proudest of and why
- the contribution that was specifically theirs within a team outcome
- feedback they have heard more than once
- work they want more of in the next role
- work they are capable of but do not want to be positioned around

Do not ask every question automatically. Read the saved answers first, identify the highest-value uncertainty, ask that question, save the answer, and reassess.

The plugin must distinguish three states:

1. **Shown:** the record supports it directly.
2. **Suggested:** a pattern appears across the record, but the person has not confirmed the interpretation.
3. **Unknown:** the record does not answer it, so the plugin asks or leaves it out.

An inference never becomes a printed self-description without the person's confirmation.

## Rewrite the whole argument before the individual lines

The document should be planned in this order:

### 1. Decide the central case

What should a reader understand about this person after the first third of the first page?

The answer should cover:

- who they are professionally
- the level and context in which they operate
- the main problems or responsibilities they are trusted with
- one or two differentiating strengths
- enough proof to believe it

### 2. Choose the evidence pillars

Select three to five themes that support the central case. Themes may include a capability, type of problem, leadership pattern, domain, scale, standard or recurring result.

Each theme needs proof. A theme with no proof is removed or turned into a question.

### 3. Give every section a job

- **Profile:** the central case in compact form, with no slogans or unsupported traits.
- **Key achievements, when useful:** the strongest proof anchors that add something the profile and role bullets do not already say.
- **Skills:** a searchable index of supported capabilities and tools, using audience terminology where honest.
- **Experience:** the cases that prove the positioning, attached to the roles where they happened.
- **Education and credentials:** the relevant foundation and required conditions, without padding.

### 4. Select before rewriting

Do not improve every fact and then try to fit them all. Choose the evidence that earns space because it strengthens the central case, answers the target or adds necessary context.

The facts ledger remains complete. The CV is the deliberate selection.

### 5. Rewrite each selected line

A strong line should normally reveal at least two of these, and more where the sentence remains natural:

- the person's contribution
- the problem, purpose or stakes
- the method or judgement that shows a strength
- the scale, difficulty or operating conditions
- the result, benefit or standard achieved

There is no single mandatory order. Start with the part that gives the reader the strongest reason to continue.

### 6. Read the document as one story

After line edits, test the whole CV:

- Can the central case be stated in one sentence?
- Do the first-page claims have proof later in the document?
- Do the strongest themes recur naturally without repeating the same claim?
- Does any section pull the reader toward a different professional identity?
- Is the person visible, or has employer language swallowed their voice?
- Would the person recognise themselves and defend every line in an interview?

## Tone controls for the language model

Before drafting, set the following controls from the person's existing writing and the target context:

| Control | Question |
|---|---|
| Confidence | How directly can the evidence be stated without inflation? |
| Formality | How formal is the person's field and existing voice? |
| Warmth | Does this document benefit from visible motivation, or should it remain primarily factual? |
| Technical density | Which field terms help credibility and search, and which would obscure meaning? |
| Pace | Should lines be compact and operational, or carry more strategic context? |
| Seniority signal | Should the emphasis be execution, judgement, ownership, leadership or organisational effect? |
| Individual contribution | What did this person do within the team result? |

These controls affect diction and sentence shape. They never change the size of the claim.

## The rewrite north star

Use this instruction before drafting any suggested CV text:

> Rewrite toward credible conviction. Make the person's strongest relevant contribution unmistakable, using language they could say aloud and evidence they can defend. Show the pattern of what they are trusted to do, how they do it and why it matters. Use the target employer's terminology where the record supports it. Prefer concrete work, context and proof over praise. Preserve useful difficulty, scale and constraints. Do not turn every duty into an achievement, force a metric, invent passion, announce a personal brand or make the person sound like an advertisement.

This instruction is the positive destination currently missing from `voice.md`. The existing file mostly defines what to avoid.

## Compact production form

The runtime version now lives in `skills/resu-studio/references/positioning.md`. It is deliberately short so the language model receives the positive target without rereading this full design argument during every application.

It incorporates the parts of the external guidance that reinforce credible conviction:

- **[Harvard](https://careerservices.fas.harvard.edu/resources/hes-create-impactful-resumes-and-cover-letters/):** select the strongest relevant assets, differentiate through evidence, tailor to what the employer values, and keep the language specific, active, clear, direct, fact-based and easy to scan.
- **[Yale](https://ocs.yale.edu/resources/writing-impactful-resume-bullets/):** show the person's own contribution, connect it to a project or problem, include the result or value where known, quantify when possible, and provide enough context to make the impact meaningful.

Neither source requires inflated language. In this strategy, their guidance is bounded by the existing truth rules: figures must already exist, verbs cannot be promoted, team results cannot be claimed as individual results, and an unknown outcome remains unknown.

## How ATS matching fits without taking over the writing

ATS work should support the central case rather than replace it.

For every important employer term:

1. Confirm that the person's record supports it.
2. Decide where it belongs naturally: profile, skills or experience.
3. Prefer the line that proves the term over a detached keyword mention.
4. Include both expanded and abbreviated forms where both are useful and supported.
5. Avoid repeating a term after the document already makes it easy to find.

The resulting CV contains searchable language and gives a human reader a reason to care about it.

## What the plugin should refuse to produce

- a slogan standing in for evidence
- a profile made from broad adjectives
- a declared passion the person did not express
- a claim of uniqueness the record cannot establish
- a page where every bullet has the same action-result rhythm
- invented metrics or inflated causality
- employer wording copied so heavily that the CV sounds like the advertisement
- a list of facts with no visible hierarchy or central case
- a polished sentence the person would not recognise as theirs

## Quality checks for the new layer

Before proposals are shown, the plugin should be able to answer:

- What is the central case this CV makes?
- Which facts prove it?
- Which repeated patterns justify the stated strengths?
- What does the person appear motivated to do, and is that stated or inferred?
- Why are these lines on the page and the omitted facts off it?
- Which employer terms were integrated, and where is the supporting evidence?
- What part of the positioning remains uncertain?
- Does the finished document sound assured and specific without becoming promotional?

If those answers do not exist, bullet rewriting has started too early.

## Proposed integration into the current workflow

1. Capture sources without editing.
2. Build the person's complete work record and the employer checklist or target brief.
3. Assess the match where an advertisement exists.
4. **Synthesize and confirm the positioning brief.**
5. Set the document's central case, evidence pillars, tone controls and page budget.
6. Propose selection, ordering and wording changes in page order.
7. Let the person accept, reject or reword each change.
8. Assemble, read the CV as a whole, recheck the match and validate ATS extraction.

Positioning therefore sits between assessment and rewriting. It guides every proposal but does not override factual traceability or the person's control.

## What success looks like

The finished CV should allow a recruiter or hiring manager to answer four questions quickly:

1. What kind of work is this person equipped to do?
2. What are they repeatedly good at?
3. What evidence makes that believable?
4. Why is that useful for this role or target market?

The document should also give the person a fifth answer: “Yes, that sounds like me.”
