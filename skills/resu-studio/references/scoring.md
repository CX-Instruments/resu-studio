# Scoring: you against it

`scorecard.md`. Run it in phase 3 before anything changes, and again in phase 6 after
the person's decisions. The movement between the two is the report.

## Seven states, and every ask gets exactly one

These seven words are the whole vocabulary. `templates/scorecard.md` bans anything
else, `scripts/render_report.py` refuses a row whose state it does not recognise, and
the studio's Score tab draws these seven and no others. One idea, one word, in all
three places.

| state | the label a person sees | what it means |
|---|---|---|
| `page` | On your CV | a line on the current draft answers it, in wording close to theirs |
| `buried` | On your CV, your wording | the work is on the page and their term for it is not |
| `off` | Left off this CV | the record answers it and this draft does not carry the line |
| `near` | Half answered | part is answered, and nothing here claims the rest |
| `missing` | Nothing to say yet | nothing in the record touches it |
| `none` | Not a CV question | settled outside the document, such as a clearance |
| `unscored` | Not checked yet | nobody has set this ask against the record |

**`buried` is the most valuable state and the hardest to produce.** It is the reason
qualified people are filtered out before a human reads them. Getting it right matters
more than the other six combined. Record their wording and the person's wording side
by side, with the fact id.

The test for `buried`: could the person describe what they did, in their own words, to
somebody who asked about this requirement, and have that person say yes, that is what
I meant? If you have to stretch to make it fit, it is `near`, or it is `missing`.

**`off` is the state worth building the whole thing for.** It only appears when the
evidence exists and the draft has dropped it, which is exactly the mistake a condensing
pass makes and exactly the one nobody notices.

**`missing` is stated plainly.** Not "an opportunity to grow". Not "consider
developing". They do not have it. Softening only moves the disappointment to after the
evening is gone, and this is the tone rule most likely to slip, because softening bad
news feels like kindness.

**`unscored` is not `missing`.** Missing means somebody looked and found nothing.
Unscored means nobody looked. An unscored ask is not evidence of anything, it must not
count toward what the person has, and it must be reported in the same breath as the
score: "sixteen of eighteen essentials, eleven asks not yet worked out" is honest,
"sixteen of eighteen" on its own is not.

## The two counts, exactly as the code computes them

Every scorecard reports two numbers and they are different on purpose. Both are counted
out of the same list of asks, and both use the same denominator.

**The denominator is every ask on the scorecard.** `none` and `unscored` are in it.
The studio counts `ASKS.length`; `render_report.py` uses `asks_total` from the
frontmatter, falling back to the number of rows in the ask table.

**What you have.** An ask in `page`, `buried`, `off` or `near`. Four states, and no
others. This number does not move when the person rejects a rewrite, because rejecting
a rewrite does not unhave the experience.

**What a reader would find.** An ask in `page`. That one state, and no others. An ask
answered only under another name does not count here until the employer's own term is
printed on the draft.

**`none` and `unscored` feed neither count.** They sit in the denominator and nowhere
else, which is why a page full of unscored asks pulls both gauges down rather than
flattering either of them.

The gap between the two numbers is what the whole exercise is for. State it in one
sentence at the top of the scorecard.

**Where the number comes from, and the one place the two implementations differ.** The
studio always tallies the list in front of it, so its gauges cannot disagree with the
rows underneath them. `render_report.py` prints the `you_have` and
`a_reader_would_find` figures out of the scorecard's frontmatter when they are there
and non-zero, and tallies the table only when they are missing. So a typed frontmatter
count that does not match the table produces a report whose gauges and whose rows
disagree, and the studio will show a third number again. Write the frontmatter counts
as the tally of the table, every time, or leave them at zero and let the report do it.

## The verdict

One of `strong`, `worth it`, `a stretch`, `not this one`, decided on the must-haves
alone. A job where somebody meets seven of eight musts and two of nine nice-to-haves
is worth an evening, and arithmetic that averages those together says otherwise and
is wrong.

The studio's own verdict line counts a must as answered when it is `page` or `buried`,
because a must the person has under another name is a must they have.

## Necessity

Five values, from `templates/scorecard.md`: `must`, `nice`, `implied`, `condition`,
`not a cv question`. `condition` is a requirement of being employed at all, such as
citizenship or a licence. Folding it into `implied` shows a hard eligibility bar as a
soft item lifted off the role description, which is how somebody spends an evening on
a job they cannot hold.

## Writing the report

Open with the honest answer in one sentence, written to them, with no heading above
it. "They have advertised the job you are already doing, in a domain you have never
worked in" lands. "This appears to be closely aligned with your current role" spends
four words getting ready to speak.

**Put what is missing first.** Gaps and partials are what somebody opens this to read.
Everything the ad does answer is confirmation, and confirmation is not news.

Then four or five findings, each opening with its point in bold and the detail
underneath, so scanning gives the answer and reading gives all of it.

Every number in the writing has to survive being counted against the lists. A verdict
saying six of eight over a scorecard showing five is the two halves of one document
disagreeing in front of the person they are for.

## Rescoring after decisions

Rescore in phase 6 and show three things:

- what moved from `buried` to `page`, which is the tailoring working
- what the person declined, and what that costs on the second count
- what is still `unscored`

Do not re-argue a rejected proposal. Report the cost once, in the count, and leave it.

## Compound asks

A split compound ask scores per part, and the report rolls it up honestly: "five of
the seven subjects in this duty are yours, two are not, and here they are". Never
score the whole duty as one thing. A person who answers five of seven is not a person
who fails a requirement.

## How deep, and who decides

**The person decides, before any of it is read, and they are told what each option
costs them.** The question and its exact wording are in `SKILL.md`, Phase 1, because it
is a gate rather than a detail and it must not end up somewhere a reader can skip.

Two things make this a real choice rather than a formality:

**Atomise the whole advertisement either way.** The ask list has to be complete or the
person is answering the wrong question. That part is cheap. It is the *scoring* that
costs, so that is the only part the choice covers.

**Expanding later costs the same as doing it now.** Say so when you ask. Somebody who
fears choosing wrong will choose the expensive option to be safe, which is the opposite
of informed.

Record the answer as `depth: essentials` or `depth: all` in the scorecard frontmatter.
Later steps read it rather than asking again, and a later session can see what was
agreed. `build_studio.py --depth` sets it when the scorecard does not say.

The studio says which depth was run at the top of its Score tab, in plain sight,
alongside what expanding would cover and what it would cost, and it counts the
essentials it actually scored rather than every essential on the list.

## Showing it to them

The scorecard is not a number. It is a list, and every count on it has to be openable
down to the ask and the line that answers it.

**The counts are computed, never typed.** They are the tally of the list underneath, so
the figure at the top and the evidence below it cannot disagree. The *state of any one
ask* is a judgement, and that is theirs to change: the row carries all seven states and
setting one recounts everything above it. That is the right split. A person may
reasonably say "no, that does not answer it"; nobody should be typing a total.

**Re-check every claim against the CV as it currently reads.** `facts.md` records what
the person's record holds. It does not know what survived the last edit, and
`scorecard.md` is where the two are set against each other. So for each piece of
evidence, find the line on the current draft that carries it, print that line rather
than the wording `scorecard.md` proposed for it, and say which role it sits under.
Where a
claim is answered across several lines rather than one, say so and show them. Where no
line carries it, say that plainly, and that ask is `off` rather than `page`.

**Two dials, and the distance between them is the argument.** One counts the asks the
record answers however worded. The other counts only the asks a line on this draft
answers in wording close to theirs. Every point of difference is a specific edit.

## What each ask offers to do

An expanded ask carries a button that does something to the CV. The state decides
which one.

| State | The button | What it does |
|---|---|---|
| `page` | Show me the line | scrolls the draft to the line and selects it |
| `buried` | Say it in their words | records that their term is missing from the line, and hands the line and the term over |
| `off` | Put the line back | records the dropped line so it can be restored where it belongs |
| `near` | I have more on this | opens a box for what they actually did |
| `missing` | Actually, I have done this | same box, and nothing is invented if they leave it empty |
| `unscored` | Check this one | queues the ask to be worked against their record |
| `none` | nothing | there is nothing a CV can do about it |

Anything they choose lands in Hand to AI with the ask, their wording and
whatever they typed, so the request arrives with its evidence attached.

## Correcting the reading is never the prominent control

Reading each ask against the record is the work the person came for. Offering to
override that reading as the first thing on the card invites them to click past the
finding instead of acting on it.

So the seven state buttons sit behind a faint vertical three-dot at the corner of the
card, closed until asked for. The card leads with the action that improves the CV. The
override stays available, because sometimes the reading is wrong and only they know it,
but it never competes for attention with the thing that helps.

## Say where a thing is, not where the label is

The first version of these labels said "this page", meaning the CV. Read on a
screen, "this page" is the screen. Every label now names the CV, so there is no
second reading: on your CV, left off this CV, nothing to say yet.
