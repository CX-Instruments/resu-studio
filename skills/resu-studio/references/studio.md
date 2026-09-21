# Studio and the writing engine

The Writing tab is the primary application entry. Read `writing-engine.md` for samples, mode selection, one generation request, publication and revision. Score, design and section controls remain part of the same Studio.

# The studio, and Phases 3, 4 and 5 in full

## Open and hand over

After a successful build, copy the generated **Resu Studio** and **Resu Desk** Markdown
links from its output into the user-facing reply as a labelled list. Use the real
absolute paths, with forward slashes and angle brackets around targets containing
spaces. In a temporary/cloud session, attach both files using that host's download
links instead. Also link any other finished HTML produced in this handoff, labelled
by purpose. Do not enumerate templates, backups, or another application's files.

On the user's own computer, open just the generated Studio with the discovered
Python and `scripts/open_studio.py "<exact path from the successful build>"`.
The helper passes a single encoded file URL directly to a browser and records one
attempt per file. Never launch the shipped `assets/studio.html` template. Never use
`start`, `Start-Process`, a shell command assembled from a path, browser-profile
creation, or a fallback/retry loop. Do not launch Resu Desk automatically as well.

A launch request does not prove a visible tab opened. If it fails or cannot be
verified, report that briefly and deliver both links. Do not try again unless asked;
`--again` is reserved for an explicit user request to reopen. A rebuild does not need
another window: update the same file and tell the person to refresh the existing tab.
In a cloud session, deliver downloads without trying to launch a desktop browser.

SKILL.md carries the short version of these phases. This is the whole of them, with
every reason behind each rule. Read the section for a phase when that phase starts.

## Rebuild the studio every time the page changes

**The studio is the only place the person sees their CV drawn.** Everything else this
skill writes is working papers. So a studio that no longer matches what they have
decided is worse than no studio at all: they open it, read it as the state of their
application, and it is out of date.

The four builds named in the phases are the minimum. One at the end of Phase 3, one in
Phase 4 with the proposals in it, one in Phase 6 from the assembled CV, and one in
Phase 7 with the letter. **The rule is larger than those four: any time something that
would appear on the page changes, build the studio again and hand the file back in the
same reply.**

What counts as a change: a suggestion they accepted, a line they rewrote in their own
words, a line taken off, a line added, a section added, a reorder of bullets or
sections, a fresh score, a different skin, and anything they asked for in the chat that
you then carried out.

**Do not wait to be asked.** They do not know the studio can be rebuilt, so it will not
occur to them to ask for one. Somebody who has just approved four changes and been
handed nothing back has no way of seeing what those four changes did to their page, and
is left taking your description of it on trust.

**Pass the same `--job <job id>` on every rebuild**, so it replaces the page
they already have instead of leaving them holding two, and pass the ledgers as well or
the Score tab opens empty. Phase 6 in `references/assemble-and-print.md`, *Pass the ledgers on this rebuild too*, has the
flags and says what goes missing without them.

Say one line with the file when you hand it back: what changed, and that this is the
same studio with the change in it.

**One moment holds a rebuild back**, and it is the one in Phase 5 where the person has
been through the suggestions and the hand-to-AI block has not come out yet. Their
decisions are in their own browser until then. Get the block out first, apply what it
says, and hand the rebuilt studio back with it.

## Phase 3 in full:: Score, before changing anything

**Score to the depth they chose in Phase 1.** On `essentials`, score every ask marked
`must` and mark the rest `unscored`. Unscored is not missing: missing means you looked
and found nothing, unscored means nobody looked. Never let one read as the other, and
never count an unscored ask toward what the person has.

Say how many are unscored every time you report a score, in the same sentence as the
number. A score of sixteen of eighteen essentials with eleven asks untouched is an
honest answer; the same number with the untouched ones unmentioned is not.

`scorecard.md`, in the job's folder. Copy the depth they chose in Phase 1 into its
frontmatter as `depth: essentials` or `depth: all`; that is where `build_studio.py`
reads it. Necessity on every row is one of five words: `must`, `nice`, `implied`,
`condition`, `not a cv question`. The studio draws all five with labels of their own,
so a citizenship or licence condition is shown as a condition of the job rather than
as a soft item lifted off the role description.

**Two of those five need a rule to tell them apart from `must`, and both rules are in
`references/atomising-sources.md`.**

- **`condition` wins over `must`.** Anything that is a condition of being employed at
  all, a licence, citizenship or a right to work, a clearance, is a `condition`, whether
  or not the advertisement published it among the criteria. A `must` is a claim about
  capability, which the application has to evidence. A condition is a yes or a no about
  the person's standing. Where the sector expects every criterion addressed, a condition
  is still addressed; it is only counted differently.
- **`implied` covers a stated duty as well as an inferred one.** A duty the
  advertisement states and does not list among its criteria is `implied`, quoted in the
  employer's own words. So is something the advertisement never writes down that a
  specific sentence gives away. What makes something a `must` is being on the list the
  application is scored against.

Every ask gets one of these states, and these are the words the studio and the printed
report both use, so all three describe an ask the same way:

| state | means |
|---|---|
| `page` | On your CV. A line answers it, in wording close to theirs. |
| `buried` | On your CV, your wording. The work is there; their term for it is not. |
| `off` | Left off this CV. The record answers it and this variant does not carry it. |
| `near` | Half answered. Part is answered and nothing claims the rest. |
| `missing` | Nothing to say yet. Nothing in the record touches it. |
| `none` | Not a CV question. Handled outside the document. |
| `unscored` | Not checked yet. Nobody has set it against the record. |

Two counts, not one: what the person has, and what a reader would find on the current
page. The gap between those two numbers is the entire value of the exercise.

**Then build the studio, at the end of Phase 3.** This is where it first exists, and
from here on it is rebuilt whenever the page changes, under *Rebuild the studio every
time the page changes* above. A rebuild for the same role, employer and CV file
replaces this same page. The Phase 6 rebuild reads a different CV file, so it keeps
this one under a dated name and says where it went, which is what you want: the score
before and the score after are both still on disk.

A table of rows is not a score anybody can take in, and this is the first moment the
person has something real to look at: their own CV, drawn, with the score beside it.
Everything up to here has been the skill's working papers.

```bash
J="$(python3 scripts/paths.py --job <job id>)"
python3 scripts/build_studio.py --cv "$(python3 scripts/paths.py --job <job id>)/<their CV>.md" \
    --scorecard "$J/scorecard.md" --asks-md "$J/asks.md" \
    --facts "$(python3 scripts/paths.py --job <job id> --facts)" \
    --job <job id>
```

The `--cv` is the markdown written in Phase 1: their CV as it arrived, converted into
the `templates/cv.md` shape and changed in no other way.

**`--job` is required.** The job's role and employer name its files and document
folder. Its random application identity and data root scope the browser decisions.
Rebuilds of that application retain them; a fresh job never restores marks merely
because its role, employer or path matches an earlier run. Building a Studio also
rebuilds Resu Desk; deliver both generated links.

The Score tab is the scorecard. It reads the three files you have just written: the
advertisement's own wording from `asks.md`, the state of each ask from `scorecard.md`,
and the verbatim line that answers it from `facts.md`. It draws the two counts, every
ask worst first, and the line on their CV that answers it. **Never build a separate
scorecard page.** There is one place a person reads their score, and it is the studio.

The studio carries its typefaces inside itself rather than fetching them from a font
server, so the preview measures its page breaks in the same metrics the print uses.

Hand it over and say what it is: their CV as it stands, scored, before anything has
been changed. The markdown files are the record behind it and are handed over too,
but the studio is the thing you point them at.

Full instructions: `references/scoring.md`.

**Done when:** the studio has been built and handed over with a populated Score tab,
everything the build said it had nowhere to put has been read and dealt with, the
person can see where they stand before a single word has changed, and the gaps are
named plainly with no softening.

## Phase 4 in full: Propose

`proposals.md`, in the person's folder. One entry per change. The `## P1.` heading
carries the location in words. Every entry then carries these fields, which are the
ones `templates/proposals.md` shows and `build_studio.py` reads:

```
Kind          which kind of change this is, one of the seven below
Line          the studio's id for the line this lands on
Currently     the full existing text, verbatim, or `Not on the CV.`
Suggested     the full replacement text, ready to paste, or `Delete this bullet.`
Why           one or two sentences
Answers       which ask ids this serves
Draws on      which fact ids this rests on
Costs         on an addition, explain growth and any explicit-limit tradeoff
Decision      left blank, for the person
```

**The entries run in page order.** Sections in the order the CV sets them out, roles in
the order they appear inside a section, bullets in the order they appear inside a role,
skills groups in the order they are drawn. Number them P1 upward in that same order, so
P1 is the first suggestion on the page and the number in the chat agrees with where the
suggestion sits. In the studio every suggestion already sits on the line it would
change, so a person working down their own CV meets each one where it lives.

**`Kind:` is what the entry is, and it no longer decides where the entry sits.** The
seven are `fix before sending`, `decide`, `same claim twice`, `cut this to make room`,
`missing and worth adding`, `wording` and `no change needed`, each explained in
`references/proposing-changes.md`. The last of those takes no number and goes at the
foot of the file, because it is the absence of a change and has no line to sit on.

**`Line:` is not optional.** It is the id `render_cv.py` and the studio both build
from the markdown, such as `professional-experience/2/b3`, `profile/0` or
`key-skills/technical`, and it is what puts the suggestion on the right line of the
page. A proposal without one cannot be shown against anything and does not reach the
person. A proposal whose `Line:` names an id that is not on this CV is left out for
the same reason, and the build names it. `references/marking.md` has the full table of
ids.

Additions say `Currently: not on the CV`, and their `Line:` is the line they print
after. Removals say `Suggested: delete this bullet` and always carry a reason.

Run the budget check and the duplication check before writing the file, not after.

**Then rebuild the studio with the proposals in it.** Same command as Phase 3 with
`--proposals` added, and the same `--job <job id>` for the reason given under
*Rebuild the studio every time the page changes* above. Their marks live in the browser
keyed to the data folder and unique job id, so nothing they have already decided is lost.

Optional achievements follow `references/achievements.md`. Publish new engine sections as explicit, evidence-mapped proposals. There is no fixed count or cross-employer requirement.

```bash
J="$(python3 scripts/paths.py --job <job id>)"
python3 scripts/build_studio.py --cv "$(python3 scripts/paths.py --job <job id>)/<their CV>.md" \
    --scorecard "$J/scorecard.md" --asks-md "$J/asks.md" \
    --facts "$(python3 scripts/paths.py --job <job id> --facts)" \
    --proposals "$J/proposals.md" --achievements "$J/achievements.md" \
    --job <job id>
```

Same `--cv` as Phase 3, because nothing has been assembled yet and every proposal sits
on a line of the CV as it arrived.

**Read what the build prints, every time. There are two things in it.**

The first is content it had nowhere to put. That is a whole section it does not know,
and now also a block inside a section it does know: a profile written as bullets, an
intro paragraph above the roles, a skills line it could not read as a group. Any of
those is a part of their CV that is not on the page, and saying otherwise is the worst
thing this skill can do. The Studio preserves additional source sections through its generic section view. A source section must never be dropped to fit a specialised editor.

The second is any proposal whose `Line:` names an id that is not on this CV. Those are
not in the studio and the person will never see them, so fix the id against the CV the
studio was built from and build again.

Then run the check.

```bash
python3 scripts/check.py --job <job id>
```

It reads the person's own folder, so it needs nothing typed after it. Exit 0 means
nothing found, 1 means faults to fix, 2 means the command line was wrong, and 3 means
the folder is not there.

Tell them it is the same studio, now with the suggestions in it. Each one sits on the
line it would change, showing the line they have and the line proposed, with five
buttons: **Use this**, **Edit it first**, **Keep mine**, **Ask for another**, and
**Take the line off instead**. Nothing is applied.

**And tell them, in the same breath, how the work gets back to you.** The studio keeps
every decision in their own browser and nowhere else. You cannot see any of it. Say
so, plainly, before they start:

> Nothing you do in there reaches me on its own. When you have been through it, open
> **hand to AI** on the edge of the page and paste the block into the chat. Or
> press **Save the decisions file** and give me `cv-decisions.json`. Then I apply it
> all to the CV at once.

A person who does not know this can work for an hour and believe it was saved,
because it *was* saved, in their browser, where nothing else can read it. Leaving
that unsaid is the single most expensive omission in this whole skill.

Full instructions: `references/proposing-changes.md`.

**Done when:** every proposal carries a `Line:` that names a line the CV actually has,
`python3 scripts/check.py --job <job id>` has been run and everything it named has been fixed or
answered, the studio has been built with `--proposals` and handed over, and the person
has been told that their CV is unchanged until they press a button in it.

## Phase 5 in full: Decide

**The deciding happens in the studio, on the page, not in this conversation.** Twenty
numbered items in a markdown file is not a decision anybody can make: they cannot see
what the line looks like where it lands, and being asked to approve a list they have
not seen is the thing this whole studio exists to prevent.

So in this phase you wait. Do not put the proposals to them one by one. Do not ask
which ones they accept. Do not offer to work through them in the chat. They open the
studio, press through the suggestions, and bring back the **hand to AI** block from
its panel, which names what they used, what they kept, what they want written again,
and anything they flagged.

**Waiting is not the same as going quiet.** Say what you are waiting for and how it
gets to you, in one sentence, every time you hand the studio over. If they come back
without the block, with a question, or a screenshot, or "I have done it", ask for
the block before doing anything else. **Never guess at what they decided, and never
ask them to tell you decision by decision in the chat.** That is the copying-out job
the block exists to spare them.

If they say the block is empty or the tab shows nothing, the decisions are still in
that browser: same page, same device, and the studio must not be rebuilt until the
block is out, because a rebuild they open on a different machine will not have them.

Three things, and only these three, are still a conversation:

- a question about a fact only they have, which follows the `answers.md` rules in SKILL.md
- something they ask you directly
- a suggestion they sent back with *Ask for another*

If they say they would rather go through it in the chat, do that. Their preference
beats this rule. But it is offered by them, never by you.

Record their decisions against the proposals when the block comes back. A rejected
proposal stays in the file marked rejected, so a later session does not raise it again.

**When they answer a question, write it into `answers.md` before you use it, and
never ask it twice.** See *Never ask the same question twice* in SKILL.md and
`references/working-with-the-person.md` for the file and
its rules. A decision on a proposal is recorded against the proposal; an answer about
their working life is recorded in `answers.md`, and the fact it produces in
`facts.md`.
When they correct you, say so plainly, fix it, and do not re-argue. Once is
information. Twice is a tool trying to win.

**Silence on a line is agreement.** The studio's final check lists the page as it then
reads, and ticking a line there is the person keeping their own place on a long page.
It is not a queue you are waiting on and it is not consent you need. **Never ask them
to go through and tick everything, never treat unticked lines as outstanding, and
never hold the CV back because the final check is not complete.** Only the suggestions
need an answer.

**Done when:** the hand-to-AI block has come back from the studio, every proposal
carries a yes, a no, or a rewording in their own words, and none of those decisions
was extracted from them in the chat.
