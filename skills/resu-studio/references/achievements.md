# Key achievements, and the other sections a CV can grow

A CV starts with five sections: profile, key skills, professional experience,
education, training and certifications. Three more can be added.

**A ticked section lives in the decisions file until Phase 6, and in the markdown after
it.** While the person is working in the studio it prints on that version, is reported as
an addition, and comes off again without a trace, because the markdown has not been
touched. Then `scripts/assemble.py` writes it into `cv-<variant>.md` as a real section,
under its own heading, in the case the file uses for its other headings. That is the
point of assembling: the file they hand over holds what they chose. From there it is an
ordinary section, so `--order` names it by its slug like any other and the studio built
from the assembled CV reads it off the markdown.

| Section | Where the content comes from |
|---|---|
| Key achievements | you draft it from their record against this advertisement |
| Professional memberships | they type it; nothing in a CV implies it |
| Volunteering and community | they type it; nothing in a CV implies it |

**Referees and eligibility are missing from that table because neither is a section.**
Referees are a short block the person types when they want one, and eligibility is a
single line under the contact block. Both are routinely fields on the application form
as well.

**Whether either goes on the page is the person's decision, put to them as a proposal
with the trade stated.** It costs a line that a criterion could have used, and where the
form already asks for it the same thing is being answered twice. Against that: where the
advertisement makes it a condition, a screener reading only the CV can see it settled
without opening anything else, and some people would rather it be visible than be asked
about it. Write both halves into `Why:`, leave `Decision:` blank, and let them answer.
Adding either unasked and stripping either unasked are both silent edits to what the
employer is told about them. `templates/cv.md`, `references/assembling.md` and
`references/marking.md` all say this the same way.

---

## Drafting key achievements

The section is a culmination. It says what this person would bring to this job, drawn
out of what they have already written. It is the first thing under the profile and it
is often the only part of the CV a busy reader finishes.

**The count, and it is one rule in three parts.**

**Draft six candidate lines.** Always six. `templates/achievements.md` has six slots
and `build_studio.py --achievements` loads whatever is there into the Key achievements
panel. Six gives a real choice; ten is a chore; four leaves them nothing to reject.

**The person ticks four to six.** Ticking four is the common landing and it is a good
outcome. Nothing prints until they tick it, and never pick for them.

**A padded sixth comes off.** If the record does not carry a sixth line at career
level, say so and let the section print five. Five real lines beat six with one
padded, and the padded one is the line a panel asks about.

### Write them at career level, not role level

**This is the rule the whole section turns on.** A key achievement condensed out of one
role bullet fails twice. It says the same thing twice on one page, and if the bullet is
removed to stop the repetition the achievement is left with no job behind it, so the
reader has a claim and nowhere to place it.

Write each line so it reaches across more than one employer. Then it says something no
single bullet says, nothing has to come off the page to make room for it, and every
role stays where it is to back it up.

Role level, and wrong:

> Held single point of accountability for every part of <the programme> at <the
> employer>.

Career level, and right:

> Accountable for <the thing> on two multi-year programmes: <the programme> at <the
> employer>, and <the other programme> at <the earlier employer>.

The second one names two employers, so no bullet under either of them says it, and both
roles stay on the page to prove it. The wording of both comes out of the person's own
lines, and this pair shows only the shape.

The shapes that work at this level:

- the same accountability held in more than one place, each named
- a span: how long, across which sectors, and what the arc was
- people led or developed in several organisations
- one habit shown three times, each instance from a different employer
- one capability built repeatedly, in whatever the business already had

**Each employer keeps its own facts.** Reaching across roles is not licence to pool
their numbers. If a figure belongs to one job, name that job in the same clause: "32+
<the things> end to end at <that employer> alone". Never let a count from one employer
read as a career total.

### Where the lines come from

Each line comes from the facts ledger, worked against the asks ledger. For each
candidate, record three things and show all three. **Write the field names exactly as
they appear here**, which is how `templates/achievements.md` has them and what
`build_studio.py --achievements` reads:

```
id: k1
text: "one sentence, their wording, condensed"
answers: which ask ids from the advertisement it speaks to
draws_on: every role it rests on, and there should be at least two
```

`draws_on:` is the one to write. `draws on:` with a space is read as the same field, so
an older file still loads, and a new one gets the underscore.

Showing the ask makes ticking a decision rather than a guess. Showing the roles is the
check on the rule above: a candidate that draws on one role has not been written at
career level yet.

### Cover the spread, not the same ground

Six achievements that all say "led delivery" is one achievement written six ways. Aim
one line at each of the essentials that carry the most weight, typically:

- the largest thing they were accountable for, and where
- the span of the career and the arc through it
- leading or developing people
- building the capability the advertisement names
- a problem they find repeatedly, and fix
- a habit with a real figure behind it

If their record does not support one of these, leave it out. That is the padded sixth
coming off before anybody sees it.

### Numbers

**Use a figure only where the record already carries it, in the form it carries it,
attributed to the job it happened in.** Eight hours to three is theirs. Thirty-two
projects at one named employer is theirs. Anything else is scope: who they answered to,
how many workstreams, which teams, over what window. A line without a number is not a
weak line; a line with an invented one is a liability in the interview.

**Check the profile too.** The profile is a summary of the same career, so a figure
that appears in both prints twice a few lines apart. If the profile already carries it,
the achievement says something else.

### The wording

Their words, condensed, in the voice of `voice.md`. No verb promotion: co-owned does
not become owned, contributed does not become led, guided does not become led. Past
tense or plain present, one sentence, no scene-setting clause at the front. The sentence
should survive being read aloud.

---

## The two checks, and neither of them deletes anything

The studio checks every ticked achievement against every line already on the CV, and
speaks up in exactly two cases:

**It draws on one role and restates a bullet.** The line has slipped back to role level.
The offer is to widen it, not to delete the bullet.

**The profile already says it.** Same claim, a few lines higher on the same page. The
offer is again to rewrite the achievement.

Neither offer removes anything from the page, because the fix is always to the added
line rather than to the record. The same holds when proposing achievements in chat:
name what a candidate doubles up on, and rewrite the candidate.

## What the section costs

Four ticked achievements is roughly a third of a page, and nothing is taken off to pay
for it.
Say the page count out loud when the section goes on, so the person is choosing with
the cost in front of them rather than finding it later.

## Sections the person fills in themselves

Memberships and volunteering are typed, one per line, because nothing in a CV implies
them and inventing either would be inventing a fact. When the person asks for help,
ask what belongs there and write it in their voice. Never offer a plausible example as
a starting point: a placeholder membership has a way of surviving into a sent
document.
