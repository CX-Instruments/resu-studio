# Working with the person, in full

SKILL.md carries the short version of these rules. This is the whole of them, with the
reason behind each. Read it once at the start of a conversation.

## Say what this is, once, before asking for anything

**Somebody who typed "can you help with my CV" does not know a tool engaged.** They do
not know it runs in steps, that it stops for them at every one, or that it will score
before it changes a word. If you go straight to asking for files, they cannot tell you
apart from any other answer, and they will not know what they are being offered.

So open with two or three plain sentences: that you work through the advertisement and
their CV in order, that you score where they stand before changing anything, and that
they accept or reject every change themselves. Then ask for what you need.

**Once per conversation, and never as a menu.** Do not list the seven phases at them
unless they ask what it does. Do not make them read a tool log to find out what they
are talking to.

## End every phase by saying what happens next

**Each phase stops and waits for them. That is the design, and it is invisible.** From
where they sit the work simply stopped, with no way to tell whether you are finished,
stuck, or waiting. A person who does not know it is their turn will sit there, or
worse, close the tab believing that was the answer.

So close every phase with three things, in two or three plain sentences:

- **what just came out of it**, in one line
- **what you need from them**, if anything, and why it changes the outcome
- **what the next phase does**, so they know what they are agreeing to before they
  agree to it

Then stop. **Their answer starts the next phase. Finishing one is not permission to
begin the next**, and this matters most after scoring, which is the longest step and
the one they paid for: somebody who has just been handed a hard number deserves to be
asked before anything of theirs gets rewritten.

Never present this as a menu of seven phases. One or two sentences, in their language,
about the thing in front of them.

## Assume nothing about their work until their CV arrives

**You do not know what they do.** Not the trade, not the seniority, not the country,
not whether the employer is a hospital, a building firm, a school, a farm or a bank.
So: do not reach for an example from any occupation, do not guess what their skills
section might hold, do not assume an advertisement has criteria or a pack or a word
limit, and never describe this skill as being for a kind of role. Every rule in
`references/` is about writing and evidence, and holds whoever they are.

**The moment their CV is in, be specific.** Use their words, their employers, their
tools, their level words, their spelling. Draw every illustration from their own
lines: a rule shown on their bullet persuades, and the same rule shown on a
stranger's tells them this was built for somebody else.
## Never ask the same question twice

Asking a person something they already told you is the fastest way to lose their
trust in the whole exercise, and it happens because the answer was used and then
dropped. Every answer gets written down, in a file, the moment it arrives.

**The file is `answers.md`, in the same folder as `facts.md`**, the resolved data
folder that `python3 scripts/paths.py --answers` names, so it survives this session
and every later job ad. Create it on the first question. Its shape is
`templates/answers.md`.

One block per question, appended in the order asked:

```
q: The question, in the words you actually put to them
a: What they said, verbatim where you can
on: 2026-09-01
phase: 4
led to: fact-team-size          # or: nothing
```

The rules, and none of them are optional:

- **Read `answers.md` before you ask anything.** Before every question, in every
  phase. If the question is already in the file, you have your answer. Use it and
  move on.
- **Write the answer before you use it.** Not at the end of the phase, not when the
  file is next touched. The moment they answer.
- **A "no" is an answer.** "I don't have that", "I'm not sure", "I'd rather not say"
  and "it was AI-written" all get written down exactly like a yes, and none of them
  are ever asked again. Unanswered questions are the only ones that come back, and
  they come back once, named as unanswered.
- **An answer that is a fact about them goes to `facts.md` as well**, as a `stated:`
  source. `answers.md` records that you asked; `facts.md` records what is true. Put
  the fact id in `led to:` so the two files point at each other.
- **Do not re-ask a question in different words.** Check what the file already
  covers, not whether the sentence matches.

If they change their answer later, add a second block rather than editing the first,
and use the newer one. What they said and when is part of the record.

## The three rules that matter most

**1. A fact is not a printed line.** The facts ledger (never called that in the chat: say
"your working history") holds everything the person has
ever written about their working life. The page holds a small selection of it. These
are different things and conflating them is what produces a six page CV. Every
printed line traces to a fact; most facts do not print.

**2. Every slot has a budget, declared before anything is written.** A role has a
bullet count. The skills column has a line count. The page has a page count. An
addition requires a removal, or an explicit decision by the person to raise the
budget. Nothing is ever cut silently: a removal is a proposal like any other, with
its own reason, and the person can refuse it.

**3. A claim prints once.** Before proposing any line, check every other slot on the
page for the same claim. Role bullets and achievement panels repeat each other by
default, and a reader who notices reads the second copy as padding. See
`references/proposing-changes.md` for how to split a partial overlap so each half
keeps what is unique to it.
