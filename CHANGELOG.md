# Changelog

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
