# Marking a line

Resu Studio is not only a place to choose a skin. Every printed line on the page can be pointed
at and decided about, and this is the part of the skill that the person actually spends
their evening in.

## What a line is

Each printed line carries a `data-id` built from where it sits in the markdown, not from
where it sits on the page. The studio and `render_cv.py` build the same ids from the same
source, so a decision made on a phone applies in a render on a laptop, and survives a
change of skin, a reorder and a repaginate.

| id | The line |
|---|---|
| `profile/0` | the profile paragraph |
| `key-skills/<slug of the heading>` | one skills group |
| `professional-experience/<n>/h` | the nth role, its title line |
| `professional-experience/<n>/s<j>` | that role's scope paragraph |
| `professional-experience/<n>/b<k>` | that role's kth bullet |
| `education/<n>`, `training-certifications/<n>` | one entry |
| `<any id>/+<n>` | a line the person wrote themselves, printed after that one |

`<n>` counts blocks of that kind inside the section, so it does not move when a section
is reordered or sent to the other column.

## The five things they can do

Point at a line and a small toolbar appears above it. Nothing types inside the sheet, so
a paginated page never reflows while they are thinking.

| | Action | What it does |
|---|---|---|
| ✓ | Read it, happy with it | takes it out of the queue and changes nothing on the page |
| ⚑ | Flag it | a coloured edge and a note to themselves. No change to the page |
| ✦ | Needs a rewrite | joins the **hand to Claude** queue, with whatever they said about it |
| ✎ | Edit it myself | their wording prints exactly as typed, the original kept in the archive |
| ⊖ | Take it off | off this version, kept in full in the archive, markdown untouched |
| ＋ | Write a new line | their line, printed after the one they pointed at |

**Never offer to write the new line for them here.** Add and Edit are their words by
definition; a rewrite is a request, and it gets answered under the same rules as
everything else in this skill: no fact, number or verb that is not already theirs.

## The two queues

Two tabs sit on the edge of the page, with counts.

**Your turn** is the review queue itself: every line not yet decided about, listed and
grouped the way the CV reads, each with a tick box and each pressable to jump to that
line on the page and select it there. It counts down as they work. Under it sits the
archive: every decision, with the original wording, and one press to undo. A
removal is not a deletion, and the archive is the point.

**Hand to Claude** is the rewrite requests. It ends in a block they copy into the chat,
which names the id, the current wording and what they asked for, then lists what they
took off, what they rewrote themselves, and what they flagged. Read that block and work
the list.

They can also save `cv-decisions.json` from that panel.

## Working and Final

A switch beside the zoom. **Working** shows the toolbar and a coloured edge on every
marked line. **Final** is exactly what prints: no toolbar, no marks, decisions applied.
Anything the person sends anyone comes from Final.

## In the renderer

```bash
python3 scripts/render_cv.py cv.md --decisions cv-decisions.json      # apply
python3 scripts/render_cv.py cv.md --decisions cv-decisions.json --marks   # and mark up
```

`--decisions` applies the removals, the rewritten wording and the added lines, and
**reports every one of them by id and by wording**, then says the markdown was not
touched. `--marks` puts the toolbar in the rendered page; it is off by default, so what
gets printed is clean. Marks made in a rendered file stay in that file: only the
studio feeds the queues.

The line count above the report is still the parse. Decisions are applied after it, which
is why they are reported separately rather than folded into the number.

## The name and the contact lines

The heading is not special. The name is `name/0` and each line of the contact block is
`contact/0`, `contact/1` and so on, so all of them can be flagged, rewritten, put in
the person's own words, taken off a version, or followed by a new line, exactly like a
role bullet.

This is what a version needs when something in the heading belongs on the application
form rather than the CV. Citizenship is the usual one: the agency asks for it in the
form, so printing it on the page spends a line and tells a reader something they did
not ask you for. Taking it off is one press, the wording goes to the archive intact,
and the markdown still has it for the next application that does want it.

**Each line of the contact block is its own line.** Consecutive lines under the name
are separate contact entries even with no blank line between them, so one can come off
without the others. They still count as the lines they are, so the in-and-out count is
unchanged.
