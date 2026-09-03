# Changelog

## 0.4.3, 3 September 2026

Two instruction changes. The seven phases and everything they do are unchanged.

**The studio comes back every time the page changes.** It was built at four named points
and nothing covered a change asked for in the chat in between, so somebody could approve
work and be handed nothing to look at. A standing rule now says that any time something
that would appear on the page changes, the studio is rebuilt and the file handed back in
the same reply, without being asked for. An accepted suggestion, their own rewrite, a
line taken off, a line added, a section added, a reorder, a fresh score and a different
skin all count. Phase 5 keeps its own rule that a studio is not rebuilt while the
person's decisions are still only in their browser.

**Suggestions are ordered by where they sit on the page.** They used to be grouped by
urgency, which sent the person jumping back and forth through their own CV. They now run
top to bottom: sections in the order the CV sets them out, roles in the order they
appear, bullets in the order they appear, skills groups in the order they are drawn, and
numbered P1 upward in that same order, so the number in the chat agrees with the position
on the page. The seven kinds of change are all kept and each entry now records its own in
a Kind field, so nothing is lost about why a change is being proposed.

## 0.4.2, 3 September 2026

Fixed pages ending several centimetres short in the middle of a CV.

A role was split for pagination into a first atom carrying the heading, the intro
paragraph and the first bullet, then one atom per remaining bullet. On a role with a
real intro paragraph that first atom is large. Measured on a real CV it came to 178
pixels, and the sheet before it had 206 pixels free, which the card's own top margin
took past the line. The whole role moved to the next page and left 5.4cm of white
behind it.

The first bullet is now folded into the head only when the head would otherwise be a
bare heading, so a heading is still never stranded on its own, and a role that carries
an intro paragraph can end a sheet after its paragraph and run its bullets on.

Measured on that CV, the sheet went from 79 percent full with 206 pixels free to 93
percent full with 75 pixels free.

## 0.4.1, 3 September 2026

Fixed the extra white space at the foot of every printed page.

The paginator measures the page on screen and then the document is printed with the
print stylesheet. That stylesheet set `line-height: normal` on the sheet, which cascaded
into every paragraph and every bullet, so the text set tighter on paper than in the
layout the paginator had measured. Each page therefore ended about a tenth of a page
above where the preview showed it ending, and the effect was the same whatever paper
size was chosen.

Measured on one document before and after: the last ink on each page moved from 76, 79
and 82 percent down the page to 85, 88 and 91 percent, and the screen and print layouts
now measure identically at 883, 958, 991 and 1034 pixels rather than the print falling
back to 814, 856, 894 and 931.

The same rule was in the studio, so the preview and the studio's own Save as PDF were
both affected. Both are fixed.

## 0.4.0, 2 September 2026

A correctness pass. An audit of 0.3.0 found 25 code defects and about 30 places where
the documentation contradicted itself or the code. An end to end acceptance test then
found ten more. All of them are fixed. The record is in `docs/audit-2026-09-02.md` and
`docs/test-run-2026-09-02.md`.

### The ones that produced a wrong document

- **The bundled typefaces were never used.** All five typesets named Georgia and
  Helvetica Neue, which match nothing in the font set, so nothing was embedded and the
  substitution check found nothing to complain about. A default PDF printed in whatever
  the machine happened to have and reported success. The typesets now name Lora, Arimo,
  Source Sans 3 and Work Sans, the faces are embedded and subset, and the check can fire.
- **A CV with the dates on their own line refused to render**, which is the shape the
  parser's own notes say almost everyone writes.
- **The studio and the renderer built different line ids** for some section headings, so
  decisions made in the studio were silently dropped at print.
- **A multi paragraph profile** was one line in the studio and several in the renderer,
  so removing it still printed paragraph two.
- **Skills edits did not print** in four of the six skills treatments.
- **The paginator measured the whole document in the fallback typeface**, because a
  browser fetches a face only when it draws text in it and every word starts hidden. It
  counted lines that were not there and broke pages early. The test CV came back from
  two pages to one.
- **Pages could be dropped or duplicated.** A skills group could vanish on a layout with
  no sidebar, two groups sharing a heading collided on one id, and a plain line under a
  labelled skills line was swallowed into the skill above it.

### Where the person's files live

- The default folder moved out of the plugin to `~/.resu-studio`, so a plugin update
  cannot delete somebody's history. Anything left in the old folder is copied out on the
  first run, never moved and never written over.
- The pointer file has a stable home outside the plugin as well, so an update cannot lose
  the pointer either. A pointer now beats the `CLAUDE_PLUGIN_DATA` environment variable.
- A Windows path or a relative path in the pointer is refused with a plain message
  instead of quietly creating a folder whose name contains the backslashes.
- `paths.py` can print one bare path for a command line, so a ledger is never written to
  a working directory that is thrown away at the end of the session.
- The employer is part of a document's identity, so two applications for the same job
  title at different employers cannot overwrite each other.

### Phase 6 assembles for real

- New `scripts/assemble.py` writes the tailored CV. It applies every rewrite, takes out
  every removal, puts in every added line, follows the order the person chose, and writes
  in every section they ticked. The result is a complete document that renders correctly
  on its own.
- `cv-<variant>-archive.md` holds every line taken off, in full, with the reason and the
  date, and both wordings of every rewrite.
- The assembled file records which decisions are already in it, so nothing is ever applied
  twice.
- A studio rebuilt on a changed CV now says on the page what carried over, what it put
  back by matching wording, and what it dropped, and keeps the previous state so it can be
  recovered.

### The studio

- `--role` is required, and the employer is in the filename and the storage key.
- Both ways of handing work back now carry the same decisions. A rejection and a question
  survive in the decisions file, and ticked achievements survive in the pasted block.
- A proposal whose right answer is a question now reaches the person instead of being
  dropped.
- The page makes no network requests at all.
- Content the studio cannot hold, and a proposal naming a line that is not on the CV, are
  both reported rather than passing silently.

### Refusals instead of guesses

- A missing paginator refuses instead of printing a blank page.
- A malformed decisions file refuses in one plain sentence instead of a stack trace.
- A page less than a quarter full is reported so nobody ships a nearly empty last sheet
  without knowing.

### Documentation

Every example identity was taken out of the shipped files. The reference files and the
templates used to carry a named employer, a named job title and a named person, some of
it apparently lifted from a real CV when the skill was first written. They now carry
placeholders in the skill's own bracket style, which also brings the files into line with
the skill's own rule against illustrating anything with an invented occupation.

Every command block published in the skill has now been run. The extraction behaviour of
all eighteen layouts was measured rather than repeated: all eight sidebar layouts
interleave once extracted, including the default, so the guidance offers the trade
instead of claiming there is nothing to trade.

## 0.3.0

The version this work started from.
