# Proposing changes

`proposals.md`. This is the file the person actually works from, so its format is not
a matter of taste.

## The entry

Every entry, without exception:

```
## P12. Current employer, Key Responsibilities, bullet 5

**Line:** professional-experience/0/b4
**Currently:**
Performed root cause analysis on complex data quality issues, translating findings into actionable remediation plans for business and technical teams

**Suggested:**
Translated root cause findings on complex data quality issues into actionable remediation plans for business and technical teams

**Why:** The achievement column already carries the root cause analysis. What it does
not carry is translating findings for two different audiences, which answers their
criterion on advice to diverse audiences. This keeps the unique half and drops the
repeat.

**Answers:** a4, a11
**Draws on:** redgate-root-cause, redgate-remediation
**Decision:**
```

The fields, in the order `templates/proposals.md` sets them out:

| Field | When it appears |
|---|---|
| `Line:` | every entry, without exception. The studio's id for the line it lands on, from `references/marking.md` |
| `Currently:` | every entry. The complete existing text, or `Not on the CV.` for an addition |
| `Suggested:` | every entry. The complete replacement text, or `Delete this bullet.` for a removal |
| `Why:` | every entry. One or two sentences |
| `Costs:` | an addition. Which existing line comes out, or "budget rises from 8 to 9, confirm" |
| `Answers:` | every entry that adds or changes text. Ask ids, and never empty |
| `Draws on:` | every entry that adds or changes text. Fact ids from `facts.md` |
| `Decision:` | every entry, left blank. It is the person's to fill in |

A removal carries `Line:`, `Currently:`, `Suggested:`, `Why:` and `Decision:` and needs
no `Answers:` or `Draws on:`, because it rests on the claim already being somewhere
else on the page and `Why:` is where that other place is named.

**An entry without a `Line:` never reaches the person.** `build_studio.py` drops it,
silently as far as the page is concerned, because there is no line to draw it against.
An entry whose `Line:` matches no id on the CV is worse: it is loaded and counted and
drawn against an empty stub, and its "Use this" writes a mark the renderer will never
match. Build the id from `references/marking.md` and check it against the render.

**Read `references/rewriting.md` before drafting any Suggested text.** It carries the
shape of a bullet, which verbs to distrust, and the named patterns to look for, which
are demonstrated on the person's own lines rather than on invented ones. Two of those
patterns end in a question rather than a rewrite, and the question is the correct
output.

**Currently and Suggested are always the complete text.** Never a fragment, never a
description of the change, never "add something about X". The person copies and
pastes. If they have to interpret it, the format has failed.

For an addition: `**Currently:** Not on the CV.` plus a line saying exactly where the
new bullet goes.

For a removal: `**Suggested:** Delete this bullet.` and a reason. Always a reason. A
line dropped quietly is how somebody sends a CV missing the thing they were proudest
of.

## Group and order

Group by urgency, not by page order, and say what each group is:

1. **Fix before sending.** Factual errors, tense left behind after a date change,
   claims the record does not support.
2. **Decide.** Places where you need a fact only the person has.
3. **Same claim twice.** Duplications, with which copy to keep.
4. **Missing and worth adding.** With where each goes.
5. **Wording.**
6. **No change needed.** Name what you checked and left alone, so the person is not
   left wondering whether you simply did not get to it.

## The budget check, before writing anything

Declare the budget first, from the current CV:

```
Redgate      8 bullets
TPG             1 role paragraph, 4 achievements
Kestrel OEL      6 bullets, 5 achievements
skills column   8 group lines
pages           3
```

**An addition requires a removal.** If you propose four new bullets for a role that
currently has eight, either propose four removals or say plainly that the role goes
to twelve and ask whether that is acceptable. Handing somebody four additions and
letting them discover the bloat themselves is the failure mode this whole skill
exists to prevent.

If the person raises a budget deliberately, record the new number and move on. It is
their CV.

## The duplication check, before writing anything

Most CVs have more than one place a claim can live: a key achievements panel, a role
paragraph, role bullets, an achievements column beside the role, and a skills block.
They repeat each other constantly and readers notice.

**Before proposing any line, search every other slot for the same claim.**

Precedence when a claim appears in two places:

- **An outcome belongs in the achievements panel.** Numbers, before and after, a thing
  that exists now and did not.
- **Scope, process and responsibility belong in the role bullets.**
- **A tool belongs in the skills block**, and appears in a bullet only when the bullet
  says what was built with it.

**Partial overlaps get split, not deleted.** Two lines that share half a claim each
keep the half the other does not have. Deleting either loses something.

Worked example. A responsibility says "Designed migration governance artefacts
including mapping specifications, transformation logic documentation, issue registers,
exception trackers, and cutover logs supporting auditability". An achievement says
"Developed comprehensive data mapping specifications and transformation logic
documentation, creating a reusable, auditable record of all migration decisions". The
responsibility contains everything the achievement does and adds three artefacts. Keep
the responsibility, cut the achievement. Reading both in full before deciding is the
only way to get this right, and reading only the first clause of each gets it
backwards.

## Ask rather than guess, every time

Put a question to the person when:

- A verb might be bigger than the record says. "Your file says you managed the
  consultant. Did you direct the partner's work, or coordinate with them?"
- A figure would make a line land and is not written down. "How many analysts? The
  line is much stronger with the number and I will not invent one."
- Two CV variants disagree.
- A claim rests on arithmetic the reader can check. See `arithmetic.md`.

A question is a better outcome than a careful rewrite of a thin line, and the answer
is usually yes.

**Read `answers.md` before putting any of these to them, and write the answer into it
the moment it arrives.** It sits beside `facts.md` in their own folder and carries
across job advertisements. A question already in that file has been answered, so use
the answer. A "no", a "not sure" and a "that was AI-written" are answers too, and are
never asked again. `SKILL.md`, *Never ask the same question twice*, has the shape and
the rules.

`answers.md` lives in the person's own folder, so pass it by absolute path:

```bash
python3 scripts/paths.py --answers
```

## The person decides on the page, not in the chat

Every proposal is written to be shown in the studio, on the line it changes. That is
why `Line:` is mandatory and why the wording of `Why:` matters: it is read beside the
suggestion, in a small card, by somebody deciding in ten seconds. One or two sentences
that say what it buys them. Not an argument.

Once the studio is built and handed over, **stop proposing and wait.** Do not walk them
through the list, do not ask which ones they accept, and do not offer a way to work
through them in the conversation. They press through the suggestions themselves and
bring back the hand-to-Claude block. Asking them to approve a list they have not seen
on the page is the failure this studio was built to prevent.

## Never

- Propose a change that answers no ask. `Answers:` may never be empty. A line that
  only reads better is a style opinion, and this is not a proofreading service. Say it
  in passing if you must, and move on.
- Propose a line that names a tool, employer, certification or standard not in the
  facts ledger.
- Propose a level the person did not write.
- Propose a figure, including a rounded, combined or "over" version of an exact one.
- Propose a defensive sentence. See `voice.md`.
- Bury a removal inside another proposal.
