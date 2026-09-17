# Marking a line

Resu Studio is not only a place to choose a skin. Every printed line on the page can be pointed
at and decided about, and this is the part of the skill that the person actually spends
their evening in.

## What a line is

Each printed line carries a `data-id` built from where it sits in the markdown, not from
where it sits on the page. The studio and `render_cv.py` build the same ids from the same
source, so a decision made on a phone applies in a render on a laptop, and survives a
change of skin, a reorder and a repaginate.

**The section prefix comes from the heading text**, lower-cased with every run of other
characters turned into one hyphen. `## PROFESSIONAL EXPERIENCE` gives
`professional-experience`, `## EMPLOYMENT HISTORY` gives `employment-history`, and
`## TRAINING AND CERTIFICATIONS` gives `training-and-certifications`. Rename the
heading in the markdown and every id under it changes with it, on both sides at once.

The skills section is the exception, and deliberately so. **Any heading with the word
"skill" in it is the skills section**, so `## TECHNICAL SKILLS AND TOOLS` is drawn as
skills rather than as plain labelled lines. Its groups keep the prefix `key-skills`
whatever the heading says, so a decision recorded against a group survives the heading
being renamed.

| id | The line |
|---|---|
| `name/0` | the name |
| `contact/<n>` | the nth line of the contact block |
| `profile/<n>` | the nth paragraph of the profile, counted from 0 |
| `key-skills/<slug of the heading>` | one skills group |
| `key-skills/<slug>-2` | a second group sharing that heading. The first keeps the plain id |
| `key-skills/group-<n>` | a skills line with no heading, `<n>` being its place among the groups in that section, counted from 1 |
| `<section>/<n>/h` | the nth role, its title line |
| `<section>/<n>/d` | that role's dates line |
| `<section>/<n>/s<j>` | that role's jth scope paragraph |
| `<section>/<n>/b<k>` | that role's kth bullet |
| `<section>/<n>` | one line of a flat list, such as education or training |
| `<any id>/+<n>` | a line the person wrote themselves, printed after that one |

`<n>` counts blocks of that kind inside the section, so it does not move when a section
is reordered or sent to the other column, and it does not move when the person reorders
the list either. A bullet keeps `b3` for as long as the markdown has it fourth.

**Which is why the ids change at the assembly.** `scripts/assemble.py` writes the
person's order into `cv-<variant>.md` and takes the removed lines out of it, so from then
on the ids belong to the assembled document. Every proposal and every note holding a
pre-assembly id is pointing at the wrong line. Close the proposals out before assembling,
and make anything new in a studio built from the assembled CV.

The duplicate-heading rule is worth reading twice. Two `**Tools:**` lines used to share
one id, so a removal took both off and neither the studio nor the page said anything.
The first keeps `key-skills/tools`, so decisions already recorded against it still land;
the second is `key-skills/tools-2`, and the render says so on stderr.

## The seven things they can do

Point at a line and a small toolbar appears above it. Nothing types inside the sheet, so
a paginated page never reflows while they are thinking.

| | Action | What it does |
|---|---|---|
| ✓ | Read it, happy with it | takes it out of the queue and changes nothing on the page |
| ⚑ | Flag it | a coloured edge and a note to themselves. No change to the page |
| ✦ | Needs a rewrite | joins the **hand to AI** queue, with whatever they said about it |
| ✎ | Edit it myself | their wording prints exactly as typed, the original kept in the archive |
| ⊖ | Take it off | off this version, kept in full in the archive |
| ＋ | Write a new line | their line, printed after the one they pointed at |
| ↑ ↓ | Move it up or down | changes where the line prints in its own list, and nowhere else |

**Never offer to write the new line for them here.** Add and Edit are their words by
definition; a rewrite is a request, and it gets answered under the same rules as
everything else in this skill: no fact, number or verb that is not already theirs.

**The arrows work on any numbered list.** A role's bullets, the education lines and
the training lines all take them, because the newest certificate belongs at the top far
more often than a bullet needs moving. The arrows do nothing on a paragraph or on a
skills group, because neither is one of a numbered list.

## The order travels with the decisions

An order made with the arrows reaches the print. It goes into `cv-decisions.json` under
a top level `order` key, and `render_cv.py --decisions` lays each list out in it:

```json
"order": {
  "professional-experience/0": [2, 0, 1, 3],
  "training-and-certifications": [1, 0]
}
```

The key is the id the lines themselves carry: `<section-slug>/<role index>` for the
bullets of one role, and the bare `<section-slug>` for a flat list. Every entry is the
line's **original** number, so `[2, 0, 1, 3]` means the third bullet of the markdown
prints first. Ids never move, which is what keeps a mark, a proposal and a rewrite
attached to the line the person pointed at while the order changes underneath them.

**A line the order does not name still prints**, in its own order, after the ones that
are named. So a partial list is a promotion and nothing can fall off the page by being
forgotten, which is why the in and out count still balances.

**A bad order is refused rather than skipped.** A number listed twice, or one naming a
line that does not exist, would print one line twice and leave another off while the
count above still balanced, so `render_cv.py` refuses to write the file and says which
key and which number. An `order` key naming a list this CV does not have cannot reorder
anything, so that one is said out loud on stderr and the render carries on.

**When several kinds of decision land on one list, they compose in this order:**
reorder, then remove, then edit, then add. The list is laid out in the order the person
put it in; a removed line drops out of that order without moving the rest; an edited
line prints its new wording in the slot the order gave it; an added line prints
immediately after the line it was written under, wherever that line ended up.

## The two queues

Two tabs sit on the edge of the page, with counts.

**Your turn** is the review queue itself: every line not yet decided about, listed and
grouped the way the CV reads, each with a tick box and each pressable to jump to that
line on the page and select it there. It counts down as they work. Under it sits the
panel holding every decision, with the original wording, and one press to undo.

**Hand to AI** is the rewrite requests. It ends in a block they copy into the chat,
which names the id, the current wording and what they asked for, then lists what they
took off, what they rewrote themselves, and what they flagged. Read that block and work
the list.

They can also save `cv-decisions.json` from that panel.

## Where the archive actually lives

The undo panel described above is a working view, and it lives in the browser's own
storage, so it goes when the tab or the device does. **The durable archive is a file,
`cv-<variant>-archive.md`, written beside the CV by `scripts/assemble.py` in Phase 6.**
It holds every line taken off, in full, with its id, its wording, the reason the
decisions file gives and the date, and every rewrite with the wording before and the
wording after. It is appended to on each pass and nothing in it is ever rewritten.

That file is what makes a removal something other than a deletion. Point at the panel
while the person is still working in the studio, and at the file from Phase 6 onwards,
which is when anybody asking where a line went can be handed something to open.

## Working and Final

A switch beside the zoom. **Working** shows the toolbar and a coloured edge on every
marked line. **Final** is exactly what prints: no toolbar, no marks, decisions applied.
Anything the person sends anyone comes from Final.

## In the renderer

```bash
python3 scripts/render_cv.py cv.md --decisions cv-decisions.json      # apply
python3 scripts/render_cv.py cv.md --decisions cv-decisions.json --marks   # and mark up
```

**A decisions file that is not shaped right is refused in plain words**, before
anything is drawn. Broken JSON names the character and says it is usually a missing
comma, a trailing comma or a quote that did not get pasted. A key holding the wrong
kind of thing is named: "marks has to be an object of id to decision, and it is a
list." This file is routinely hand saved out of a pasted block, so a small shape error
is likely, and it used to arrive as a Python traceback in the middle of a render.

On a markdown that has not been assembled, `--decisions` applies the order, the removals,
the rewritten wording and the added lines. On an assembled one it recognises the
decisions the file already holds and applies nothing, and says so in one sentence.
`--marks` puts the toolbar in the rendered page; it is off by default, so what gets
printed is clean. Marks made in a rendered file stay in that file: only the studio feeds
the queues.

## Which command reports what

**`scripts/assemble.py` is where the changes are reported now.** It is the run that makes
them, so it is the run that names them, and after it the render has nothing left to apply
and reports none of it.

| kind | what `assemble.py` prints |
|---|---|
| a rewrite | counted in the summary line, and written into the archive with the wording before and after |
| a removal | counted, then each line by id and by its full wording, and written into the archive in full |
| an addition | counted, then each line by the id it prints after and by its wording, truncated to fit the terminal |
| a reorder | counted, then each list by id, as the original line numbers in the order they now print |
| a section written in | counted, then named by its title |

It also names, on stderr, any mark or addition in the decisions file that this CV has no
line for.

**The render's own report is for the un-assembled case only**, where `--decisions` is
doing the applying. There it prints `taken off by your decisions`, `added by you` and
`put in the order you chose`, and it says nothing at all about a rewrite, so a run that
applied four rewrites and one removal reports one line while the count above it still
reads "31 content lines in, 31 out". **Do not read that report as a full account of what
the decisions file did.** The full account is what `assemble.py` printed, and the wording
of everything including the rewrites is in `cv-<variant>-archive.md`.

The line count above either report is the parse of the markdown. Decisions are counted
after it, which is why they are reported separately rather than folded into the number.

## The name and the contact lines

The heading is not special. The name is `name/0` and each line of the contact block is
`contact/0`, `contact/1` and so on, so all of them can be flagged, rewritten, put in
the person's own words, taken off a version, or followed by a new line, exactly like a
role bullet.

This is what a version needs when something in the heading belongs on this application
and not the next one. Citizenship is the usual one. **Whether it prints is the person's
decision and it is put to them with the trade stated**, like every other change in this
skill. On one side, the line costs space a criterion could have used and the form
usually asks for the same thing in a field of its own. On the other, where the
advertisement makes it a condition of employment, a screener reading only the CV can see
it answered without opening anything else. Never take it off on their behalf and never
add it on their behalf: both are silent edits to what the employer is told about them.

Taking it off is one press, and the wording survives twice over: the assembly writes it
into `cv-<variant>-archive.md` in full, and the CV as it arrived still carries it in
`cv-source/` for the next application that does want it. `templates/cv.md`,
`references/assembling.md` and `references/achievements.md` all say this the same way.

**Each line of the contact block is its own line.** Consecutive lines under the name
are separate contact entries even with no blank line between them, so one can come off
without the others. They still count as the lines they are, so the in-and-out count is
unchanged.
