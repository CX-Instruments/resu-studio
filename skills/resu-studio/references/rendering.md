# Rendering

Two renderers, both optional, both last. Neither can change what a document says.

```bash
python3 scripts/render_cv.py cv-data-reporting.md --decisions cv-decisions.json \
    --layout sidebar-dark --palette forest
python3 scripts/render_cv.py cv-data-reporting.md --decisions cv-decisions.json \
    --gallery --outdir skins-samples
python3 scripts/render_cv.py --list
python3 scripts/render_report.py scorecard.md --before scorecard-before.md
```

**`--decisions` goes on every render from the moment the file exists**, and what it does
depends on whether the markdown has been assembled.

**On an assembled CV it applies nothing.** `scripts/assemble.py` writes the removals, the
rewordings, the added lines, the order and the ticked sections into `cv-<variant>.md`
itself, and leaves one HTML comment on the last line saying which decisions are in there.
The render reads that comment, recognises the decisions it has been handed, applies none
of them and says so in one sentence, so nothing prints twice. Rendering an assembled CV
with no `--decisions` at all produces the correct document. Keep passing the flag anyway:
a person can mark up a studio built from the assembled CV, and those decisions are
relative to the assembled document and do apply normally.

**On a markdown nobody assembled it does the applying**, and it is what carries the
removals, the person's own rewordings, the added lines, the order they put the lines in
and any section they added. A render of such a file without it prints the markdown alone,
so the deleted bullet comes back, the added lines are gone and the reorder is undone, and
the line count still balances because the markdown really does account for every one of
its own lines. Nothing on screen says the document is wrong. The path is written out in
full in `SKILL.md`, against the person's own data folder.

**A decisions file changed after it was baked in stops matching the note**, which records
what the file does to the page rather than its bytes. Its additions then print twice and
its reordered lists shuffle a second time. The run says so on stderr and names the ids.
The answer is to assemble again from the source.

Where there is no decisions file, because the person handed their work back as the
pasted block instead, the markdown has to already carry everything they decided, and
that is worth saying out loud rather than assuming.

**The render no longer reports what the decisions did on an assembled CV**, because it
did nothing. `assemble.py` is the run that names every rewrite, removal, addition,
reorder and section, and `cv-<variant>-archive.md` holds the wording of all of it.
`references/marking.md` has the table of which command prints what.

`render_report.py` takes the scorecard, an optional `--before` and an optional `--out`.
It has no `--palette`. Its own docstring used to advertise one, which is why it turns
up in older command blocks; passing it now is an error.

## Do not choose a skin by reading this file

There is a studio. It draws the person's own CV live, on a phone or a laptop, with
every layout, palette, typeface, skills treatment, section order and column placement
as a control, and it prints the exact command line for whatever they land on. Send them
there and render what they choose. Guessing on their behalf and showing them one render
is how the last version of this wasted an evening.

The studio is one HTML file holding the CV as data. There is nothing to publish and no
link to send: `build_studio.py` writes the file into the person's own documents folder
and it is handed over as a file, which is why it carries everything it needs inside
itself and works with no network. Rebuild it from the current CV when the wording
changes, and hand over the rebuilt file.

`--role` is required. It names the file and it keys this application's own browser
storage, so a line marked in one application does not turn up in another.

```bash
python3 scripts/build_studio.py --cv "cv-<variant>.md" --role "<the job title>" \
    --employer "<the employer>" \
    --facts "$(python3 scripts/paths.py --facts)"
```

**Pass a ledger with command substitution.** A bare relative path resolves against
whatever directory the session happens to be in, and that directory does not outlive
the session. `scripts/paths.py` prints the real one:
`--data`, `--facts`, `--answers`, `--documents` and `--cv-source` each print one bare
path and nothing else.

## The faces

`assets/fonts.json` holds the twenty-one faces a CV can be set in. Headings and body
text are chosen separately:

```bash
--head-font oswald --body-font work-sans --size normal
```

**The faces are carried inside the document, as base64, from `assets/fonts/`.** That is
the only account of how a font reaches the page, and it is what makes the PDF
trustworthy: the page draws the same letters on a machine with no network at all, which
is where PDFs usually get made. A page that names its typefaces and fetches them from a
font server prints correctly only where that server is reachable; everywhere else the
browser substitutes quietly, the metrics change, the page breaks move, and the file
still looks finished.

Eighteen of the twenty-one families are bundled, both weights each, and the renderer's
matcher resolves every one. The other three, Arial, Times New Roman and Verdana, are
the machine's own and are never fetched or carried. They are the one case where the
file depends on what is installed, so a skin built on them prints exactly only where
those faces exist.

A `<link>` to a font server is emitted only for a family that has no file bundled, so
on the shipped skill it is emitted for nothing at all.

**The five typesets name real bundled families**, so a default render actually embeds
its fonts and the substitution refusal has something to check. This is the change that
makes every promise below hold on the default path rather than only when
`--head-font` and `--body-font` are passed:

| Typeset | Label | Headings | Body | Scale |
|---|---|---|---|---|
| `serif` | Serif | Lora | Lora | 1.0 |
| `sans` | Sans | Arimo | Arimo | 1.0 |
| `mixed` | Serif heads | Lora | Source Sans 3 | 1.0 |
| `mixedalt` | Sans heads | Source Sans 3 | Lora | 1.0 |
| `tight` | Tight sans | Work Sans | Work Sans | 0.94 |

`mixed` is the default. All four families are in `assets/fonts/` at 400 and 700.

`--size small|normal|large` scales the whole document by 0.94, 1 or 1.06. `--typeset`
sets both faces at once; `--head-font` and `--body-font` override it.

**In the studio every face is labelled in itself.** A list of font names set in one font
tells you nothing, which is the whole reason for showing them that way.

## Choosing how the skills read

`--skills` sets the default drawing for every skills group:

| Value | What prints |
|---|---|
| `list` | the grouped lines exactly as the markdown has them. The default |
| `columns` | the same lines, split into two columns |
| `bars` | one row per rated skill, with a bar |
| `dots` | one row per rated skill, with five dots |
| `rings` | a grid of small rings, one per rated skill |
| `chips` | every skill as a tag, tinted by the level it states |

**One treatment for all eight groups looks lazy, and it is.** A group of six rated
tools earns a scale; a Domain group with no levels in it does not. So the default is
only a default: `--skills-by "Technical=bars;Languages=list"` sets a group by its
exact heading, and anything not named falls back to `--skills`.

`--skills-order "Languages;Technical;..."` sets the order the groups print in,
by their exact headings. Anything it does not name keeps its own position at the end,
so a partial list is a promotion rather than a rewrite.

`--skills-place "Domain=main;Systems and platforms=side"` sends single groups to the
other column. **The skills section does not have to sit in one column.** The Key skills
heading stays where the section itself is placed by `--order`, and a group sent across
prints in the other column under its own bold heading rather than repeating the section
heading. On a layout with no sidebar the flag keeps the group in the main column and
says so on stderr, because there is nowhere to send anything.

`--hide-groups "Domain;AI and emerging tools"` leaves named groups off this version,
matched on their exact headings. **It is never silent.** The run prints what it took off
and how many skills went with it, says that the line count above it is the parse rather
than what printed, and warns on stderr if a heading was named that no group has. Use it
for a version of the CV, not for tidying: a group that is wrong belongs out of the
markdown.

`--gap tight|normal|airy` sets the space between groups. `--no-legend` drops the line
that says what the five steps are, which should only be dropped when no group is drawn
on a scale.

### Which heading is the skills section

**Any heading with the word "skill" in it.** `KEY SKILLS`, `SKILLS`, `TECHNICAL SKILLS
AND TOOLS` are all drawn as skills, by the renderer, by `build_studio.py` and by the
studio, using the same test in all three. A CV headed `TECHNICAL SKILLS` used to be
drawn as skills in the studio and printed as plain labelled lines here, under a
different id on each side, so every decision the person took about one of those lines
landed on an id the renderer never built.

The id prefix does not follow the heading. Skills groups are addressed as
`key-skills/<slug of the group heading>` whatever the section is called, so a decision
survives the section heading being renamed. Every other section takes its prefix from
its own heading.

**A second group sharing a heading carries an occurrence number.** Two `**Tools:**`
lines used to share `key-skills/tools`, so one removal took both off. The first keeps
the plain id, the second is `key-skills/tools-2`, and the run says so on stderr. **A
skills line with no heading gets a positional id**, `key-skills/group-<n>`, `<n>` being
its place among the groups counted from 1, rather than every unlabelled line collapsing
onto one empty id.

### The rule the drawings are built on

**A bar, a dot or a ring is drawn only where the markdown states a level.** There is no
default level, no inferred level and no average. Skills with no stated level print as a
line of text under the graphic, in their own words, so nothing is lost and no number
appears on the page that its owner did not put there. Anything in brackets that is not
a level, "10+ yrs", "personal development projects", travels with the skill.

**Every treatment prints the level as text.** Bars, dots, rings and chips all put
`A skill (Advanced, 10+ yrs)` on the page as characters beside the drawing, so a
screener extracting the PDF gets the level whether or not the graphic means anything to
it. Checked by extracting the text out of a printed PDF in each of the six treatments.

## Section order and which column

`--order` takes the section headings as slugs, in the order they should print, each
optionally with `:side` to send it to the sidebar:

```
--order profile,key-skills:side,professional-experience,education,training-and-certifications
```

A slug is the heading lower-cased with every run of other characters turned into one
hyphen, so `## TRAINING AND CERTIFICATIONS` is `training-and-certifications`.

With no `--order`, skills, education, training and certifications, certifications and
eligibility go to the sidebar by their titles and everything else stays in the main
column. Rename a section in the markdown and it moves.

`:side` only does anything on a layout that has a sidebar. A section the flag forgets
still prints, last, in the main column, and the run says so. **The renderer never drops
a section.** Taking something off the page is an edit to the markdown, never a flag,
for the same reason the line count is enforced.

`--group own|discipline|strength` regroups the skills without rewording them. `own`
keeps the headings as written. `strength` regroups by the level each skill states.
`discipline` reads `assets/regroup.json`, which maps new headings to the ones in the
markdown; with no such file it falls back to `own` and says so.

## The order the person put the lines in

`--decisions` carries a top level `order` key, written by the studio's up and down
arrows, and the renderer lays each list out in it, so a bullet the person moved on
screen prints where they moved it. After the assembly the lines are already in that order
in the markdown, so the render lays them out as it finds them and applies the key to
nothing.

```json
"order": {
  "professional-experience/0": [2, 0, 1, 3],
  "training-and-certifications": [1, 0]
}
```

The key is the id the lines themselves carry: `<section-slug>/<role index>` for the
bullets of one role, and the bare `<section-slug>` for a flat list such as education or
training. Every entry is the line's original number, so `[2, 0, 1, 3]` prints the third
bullet of the markdown first.

**Ids never move.** Only the slot a line prints in moves, which is what keeps a mark, a
proposal and a rewrite attached to the line the person pointed at. A line the order does
not name keeps its own place at the end, so nothing falls off the page by being
forgotten and the in and out count still balances.

**Several kinds of decision on one list compose in this order:** reorder, then remove,
then edit, then add. The list is laid out in the order given; a removed line drops out
of that order without moving the rest; an edited line prints its new wording in the slot
the order gave it; an added line prints immediately after the line it was written under,
wherever that line ended up.

An order naming a line twice, or naming one that does not exist, is refused rather than
skipped, because skipping it would print one line twice and leave another off while the
count still balanced. An `order` key naming a list this CV does not have is said on
stderr and the render carries on.

## The contract, and how it is enforced rather than promised

**Reads the markdown and nothing else.** No ledger, no notes, no proposals file. The
old workflow rendered from the history files, which is how a reviewer's working notes
printed on a finished CV. The renderer cannot reach them because it never opens them.

**Adds nothing, drops nothing.** `render_cv.py` counts the content lines in the source
and the source lines the parsed document accounts for. **If the two differ it refuses
to write the file** and says so. Not a warning, not a note in the output, a refusal.
Every run prints the pair, for example "78 content lines in, 78 out".

**Never loses a line off the bottom of a page, and the guarantee is a runtime one.**
There is `overflow:hidden` in this stylesheet, there are fixed heights in it, and there
is absolute positioning in it: a sheet is 297mm tall and clips, the sidebar and the main
column are `height:100%`, and `rail` and `spine` hang dates in the margin absolutely.
Those are what make an A4 sheet an A4 sheet. What protects the content is not the
absence of those rules but the paginator's check on the way out: before laying out, it
takes the set of `data-id`s in the source, and at the end every one of them has to be on
a sheet. If any is missing it throws the whole pagination away and prints the document
on one long sheet instead, because a visibly long page is a problem somebody can see and
a silently dropped line is not. Nothing is ever both hidden and gone.

**A missing paginator is a refusal rather than a blank page.** All the content is
written into a hidden block and the paginator is what moves it onto the sheets, so
without `assets/paginate.js` the file would open at the right size with nothing on it.
`render_cv.py` checks for it before writing anything and says what is missing and what
to restore. The page also carries a `<noscript>` rule that shows the unpaginated
document as one long column, so a browser with JavaScript off shows the CV rather than
white paper.

**A malformed decisions file is refused in plain words.** Broken JSON names the
character and says it is usually a missing comma, a trailing comma or a quote that did
not get pasted. A key holding the wrong kind of thing is named as well: "marks has to
be an object of id to decision, and it is a list." That file is routinely hand saved
out of a pasted block, so a small shape error is likely.

**Preserves levels and figures.** Levels live in brackets inside the text, so nothing
can drop them by expecting a number and finding the word Advanced. That happened
before and it happened silently.

**Skins are CSS only.** A layout, a palette and a typeset change appearance. None of
them can add, remove or reword a line, because they are variables and class names
applied to identical markup.

## Pages, and where they break

**The output is a stack of real A4 sheets, not one long scroll with dashed lines
drawn on it.** `assets/paginate.js` runs in the page, measures each sheet, and moves
finished blocks onto the next one. Both renderers inline it, so what the studio shows
and what a browser prints are the same document.

What it will not split:

| Unit | Behaviour |
|---|---|
| a bullet | moves whole to the next sheet |
| a role heading | travels with its scope line and its first bullet |
| a skills group | moves whole, headings and items together |
| a section heading | never printed alone at the foot of a sheet |
| a labelled line, a training entry | moves whole |

A block taller than a whole sheet is not clipped. That sheet grows instead, because a
long page is a problem you can see and a clipped one is not.

Sheets sit on a grey ground with a gutter between them on screen, and `break-after:page`
sends each one to its own sheet when printed.

## Page count

The renderer does not enforce a page limit and does not try. It cannot know the
reader's paper size or margins, and a renderer that trims to fit is a renderer that
edits. `--pdf` prints the file and reports the page count of the finished PDF, which is
the true one.

If the CV runs past the limit, that is a content decision, so it goes back to phase 4
as proposals with reasons, where the person can accept or refuse each cut.

## Skins

18 layouts, 10 palettes, 5 typesets, so 900 skins. `--list` prints them.

| Layout | What it is |
|---|---|
| `sidebar-dark` / `sidebar-right` | full-height dark sidebar, left or right |
| `sidebar-tint` / `sidebar-tint-right` | the same in a tint rather than a dark fill |
| `sidebar-line` / `sidebar-line-right` | no fill at all, one hairline between the columns |
| `sidebar-top` / `sidebar-top-right` | sidebar on page one only, then a tint edge |
| `band` | dark header band across the top of page one |
| `slab` | dark slab, section headings floated into the gutter |
| `panel` | the header inside a ruled box, headings with an accent bar |
| `spine` | timeline down the left with a dot per role |
| `cards` | each role in its own tinted card |
| `rail` | dates and section headings in a left gutter |
| `bands` | each section heading a full-bleed tint band |
| `classic` | centred, ruled, conservative |
| `compact` | two-up header, tighter leading, skills in two columns |
| `hairline` | wide margins, thin rules, quiet |

Palettes: ink, forest, navy, slate, oxblood, teal, plum, sand, copper, mono.
Typesets: serif, sans, mixed, mixedalt, tight.

`--layout sidebar-dark --palette forest --typeset mixed` is the default skin.

**`--gallery` renders the person's own CV in every layout and palette on one page**,
scaled down, so the choice is made by looking rather than by reading names. Pick one,
then render it properly.

**Every layout carries through past page one.** A layout that only styles the first
sheet is a bug, not a design: check the top margin, the left margin and the treatment
on sheet two before adding one. Header devices that belong to page one alone (the band,
the slab, the sidebar on `sidebar-top`) leave the following sheets a normal margin and,
where the layout has a colour, a trace of it: `sidebar-top` runs an 8mm tint edge down
the later pages so they read as the same document.

**A section heading that lands at the top of a sheet drops its top margin**, in every
layout, so page two starts where page one starts.

**A skills row is one line: the name at one end, the drawing at the other.** That
holds in every layout, `classic` included. Stacking the drawing under the name, or
centring both, wastes a line each and reads as a different document. `classic` centres
the group headings and the rings, because those are blocks rather than rows, and leaves
the rows alone.

**The narrow column is the exception, and only for bars.** In a 35% sidebar a 26mm bar
leaves the name wrapping four lines deep against a bar hanging in the middle of it, so
inside `.aside` a bar row gives the name the full width and puts the bar under it. Five
dots are 40px wide and need no such thing, so a dot row stays on one line in the
sidebar too, name left and dots right, like everywhere else. The row carries `bar` or
`dot` in its class so the two can be told apart in CSS.

Every sidebar layout shares one block for this, `ASIDE_SK`, so a new sidebar layout
cannot quietly miss out: `sidebar-top` did miss out, and drew the wide row in a narrow
column until it was noticed.

## Group the studio by what the layout does

Eighteen layouts in one long list is a wall. They sort into four families by the shape
of the page rather than by name, and each family gets a plain-English line: a column
beside the page, a block across the top, something down the side of the roles, nothing
but type. Pairs that differ only in which hand they sit on stay next to each other, so
`Sidebar, page one` and `Sidebar, page one, right` are side by side rather than three
rows apart.

## The report

`render_report.py` reads `scorecard.md` and draws:

- **Two gauges.** What you have, measured against the facts ledger. What a reader
  would find, measured against the page as it stands. They are separate because they
  are different questions, and showing one number instead of two is the mistake this
  workflow exists to avoid. Which states feed which gauge is in `references/scoring.md`.
- **The gap between them** in one sentence, which is the case for doing the work.
- **A bar for each state**, with "Not checked yet" drawn separately from "Nothing to say
  yet", because one means nobody has looked and the other means the answer is no.
- **The ask by ask table**, with evidence ids, so any row can be traced.

```bash
python3 scripts/render_report.py scorecard.md --before scorecard-before.md
```

`--before <earlier scorecard>` puts a hollow marker on each gauge showing where it
stood before the person's decisions. That is the movement, and it is the honest way to
show it: the left gauge barely moves, because rewriting does not change what somebody
has done. The right gauge is the one that moves.

The report computes nothing of its own where the scorecard has already said it. It
prints the frontmatter counts when they are there, and tallies the ask table only when
they are missing, which is why the frontmatter counts have to be the tally of the table.

**A row that does not line up is refused rather than drawn.** Every row needs all five
cells, because the columns are read by position and one missing cell shifts every later
cell one to the left. The refusal names the line and shows the shape.

## If you use a different renderer

Fine, as long as it honours the contract above. If it cannot, prefer the markdown. A
CV the person can paste into anything beats a designed one that quietly disagrees with
its own source, and this workflow has already produced one of those.

## Sections the person added

**This is how an added section reaches the page before Phase 6.** After the assembly it
is a real section in `cv-<variant>.md`, written there by `scripts/assemble.py`, and the
renderer reads it off the markdown like any other section.

Until then, `--decisions` carries sections that are not in the markdown. The studio
writes them into `cv-decisions.json` under `sections`:

```json
"sections": [
  {"id": "achievements", "title": "Key achievements", "slug": "key-achievements",
   "after": "profile",
   "lines": [{"key": "key-achievements/a1", "text": "..."}]}
]
```

`after` is the slug of the section it follows, so the added section lands where the
person put it. Every line keeps the key it had in the studio, so marking, removing
and the archive work on it exactly as they do on a line from the markdown.

**They are spliced in after the line count, never before.** An added section carries no
source lines, so `78 content lines in, 78 out` still describes the markdown alone and
cannot be inflated by an addition. The added lines are then reported under their own
heading, `added by you`, with the reminder that the markdown was not touched.

The heading follows whatever the file does with its own: if every `##` in the markdown
is uppercase, the added one is uppercased too.

`--order` names an added section by its slug like any other, so it can be moved or sent
to the sidebar. Leaving it out of `--order` prints it last in the main column rather
than dropping it, same as every other section.

## Measure the page the reader gets, not the one the atomiser made

To lay a CV on sheets the paginator cuts it into atoms: a role becomes its heading plus
one atom per bullet, so a bullet is never sliced in half by a page edge. Atoms that land
on the same sheet are then stitched back into one block.

**Stitching has to happen while the sheet is filling, not after it.** A role card
carries its own padding, border and bottom margin. Six bullet atoms measured one at a
time are six sets of that chrome, about three hundred pixels more than the single card
they become once stitched. Fill on the pre-stitch measurement and the sheet declares
itself full while half of it is still blank, then the stitch collapses it and the hole
is what prints. On one draft that cost `cards` three whole pages and left gaps of
up to 590px mid-document; merging during the fill brought it to 5 pages with nothing
over 150px.

So `fill` merges each atom into the block above it when they share a group, measures
that, and unmerges cleanly if it does not fit. A gap on a finished page should be about
one atom tall. Anything much larger is this bug coming back.

**The safety check counts lines, not atoms.** Atoms merge as the sheet fills, so their
count means nothing by the end. Before anything is split, the paginator takes the set of
`data-id`s in the source; at the end every one of them has to be on a sheet. If any is
missing it throws the pagination away and prints the whole CV on one long sheet.

## Absolute gutters need a width the content fits

`rail` and `spine` hang dates and headings in the margin with `position:absolute` and a
fixed width. A date longer than that width does not wrap by default, because
`.roledates` is `white-space:nowrap` in the base: it overflows to the right and prints
on top of the role title. "Aug 2022 to May 2023" is 111px at 8pt; the gutter was 79px.
Any layout putting text in a fixed-width gutter has to set `white-space:normal` and a
width the longest real value fits, and be checked against a date range rather than a
bare year pair.

## Two columns for a flat list

`--columns education,training-and-certifications` runs those sections in two columns.
Only flat lists take it: a set of short lines, one per item. A paragraph cannot, roles
cannot, and skills has its own treatment.

The paginator splits a `.cols2` box the way it splits a list, one atom per item, and
rebuilds the box on whichever sheet the items land on. So a nine-item list can print six
items in two columns at the foot of one page and three at the top of the next, and each
sheet's box lays itself out.

In the studio the same thing is the 1 col / 2 col button on the section's row, and it
writes `--columns` into the copied command.

## A block beside a float still spans the full width

Only the line boxes inside a block avoid a float. The block's own box does not: it runs
the full column width, straight under the panel. Nobody notices until the block has a
background, a border, or a selection outline, and then the outline for one bullet draws
a rectangle across the sidebar and it looks broken.

`display:flow-root` on each block beside the float fixes it: the block gets its own
formatting context, shrinks to the space left, and its outline stops where the panel
starts. Blocks below the float take the full width as before.

## The panel takes a whole section or none of it

`sidebar-top` and `sidebar-top-right` put the sidebar on the first sheet and nowhere
else. That is the layout rather than a bug: the skills column earns its place beside the
profile, and by page two the reader is in the roles and the width is worth more than the
panel. The following sheets keep an 8mm tint edge so they still read as the same
document.

`sidebar-top` has one page of panel and no more. The first attempt let the panel hold
what fitted and pushed the rest into the document, and it looked exactly like what it
was: a list chopped in half, with no way for a reader to know the two halves are one
thing. Repeating the heading on the continuation made it legible and still wrong.

So the panel is tried whole. The paginator lays the sidebar out on a throwaway sheet
first; if the section does not fit entirely, the sheet is discarded, the source is
re-atomised, and the panel keeps only the name block while the section prints full
width in the document. Either a proper sidebar, or a name plate and no sidebar at all.
Nothing is ever half in and half out.

**Where the section goes when it comes out of the panel** is the person's section order,
not the top of the page. The builder leaves a `<div class="spill" data-spill="<slug>">`
in the main flow at the place each side-placed section would have occupied; the
paginator matches each moved section to its own marker by the slug of its heading. Pile
them all at the first marker instead and education lands ahead of the roles.

The full-height sidebars are a different case and still carry a section across pages,
because there the sidebar continues on the next sheet and the reader can see it does.

## The cover letter wears the same skin

`--letter <file.md>` renders a cover letter instead of the CV, on whichever skin is
selected, taking the name and contact block from the CV file. Two documents that arrive
together and look like they came from different people undo each other, so the
letterhead has one source and cannot drift.

**On a sidebar skin the date and the addressee ride in the column with the name.** That
is what a letterhead column is for, and it is also what stops a 430 word letter running
to a second page in a body two thirds of the page wide. Without it every sidebar skin
spilled three lines onto page two.

**A letter has no section headings, so the layouts that keep a gutter for them give the
gutter back.** `slab`, `spine` and `rail` all reserve 30mm or more down the left for
headings that a letter does not have; `LETTER_FIX` returns it, which is what takes
`slab` from two pages to one.

All eighteen layouts print this letter on one page. That is the bar: if a layout cannot,
the layout is wrong for a letter, not the letter.

## Save as PDF from inside the studio

One button, at the top of the page beside the zoom. It prints each document in turn,
straight from the studio page, and the browser's own Save as PDF writes the file. The
browser's own print, from the menu or the keyboard, does the same thing.

**The sheets have to be moved into the studio document first.** They are laid out inside
a frame, and a browser prints a frame as one box and clips whatever does not fit. So a
`beforeprint` handler copies the finished `#doc`, and the stylesheets it needs, into a
`#printarea` that sits directly under `body`. `afterprint` empties it again. Because the
copy hangs off `beforeprint` rather than off the button, a person who reaches for the
print menu gets the pages too.

**And the studio itself has to get out of the way.** `@media print` hides `body > .app`
outright and releases the `100dvh` grid, `overflow:hidden` and dark background that the
studio needs on screen. Without that release, a print of the studio page came out as the
tabs and the rails, which is what a first attempt did.

**Do not test in-page printing headless.** `window.print()` in a headless browser does
nothing, so the test looks like a blank page and says nothing about the real one. Test it
by dispatching `beforeprint`, switching the page to print media, and printing to PDF from
the test harness. That measures the CSS, which is the part that can be wrong.

**It has to be the real page, not a PDF the page draws.** A PDF generated inside the
studio cannot use the chosen typeface, because the sandbox will not let it fetch a font
file, and a rasterised one has no text in it at all, which is useless to a keyword
screener. Printing the document itself keeps the real faces, the real colours and
selectable text.

**When the browser will not print at all,** the third route is the most reliable of the
three: **Copy settings**, the button next to Save as PDF on the bar above the page,
handed to Claude, who runs `render_cv.py` and writes both PDFs into the person's folder.
The button is on the bar rather than on a tab, so it is there whichever tab is open and
whether the view is Working or Final.

## Printing to PDF

`--pdf` is the last step. It writes the HTML exactly as it always did, then hands
that file to a real browser and asks the browser to print it.

```bash
python3 scripts/render_cv.py cv.md --letter cover-letter.md --decisions cv-decisions.json \
    --layout sidebar-dark --palette forest \
    --role "<the job title>" --employer "<the employer>" --pdf
python3 scripts/render_cv.py cv.md --decisions cv-decisions.json \
    --pdf --pdf-dir "<the folder they asked for>"
```

One run writes every document it was given. They are posted together, so they are
printed together, and the layout, palette and typeset on this command are the ones the
person chose for the CV. A letter on a different palette reads as somebody else's letter.

**A `--letter` run writes the letter's HTML and does not rewrite the CV's.** Both PDFs
are written, and the CV's named HTML file is left exactly as the last CV render made it.
So a CV HTML produced earlier without `--decisions` sits in the person's folder with the
deleted bullet still in it, beside a PDF that is correct, under a plainer name than the
PDF has. Either render the CV on its own with `--decisions` so that file is right too, or
take the stale HTML out of the folder before handing anything over.

### What the files are called

`_pdf_names` builds the name out of five parts, joined with " - ", and leaves out any
part with nothing in it:

```
<Full name> - <role> - <employer> - <date> - CV.pdf
<Full name> - <role> - <employer> - <date> - Cover Letter.pdf
```

The role is `--role`, the employer is `--employer`, and the date is `--date` or today
as `YYYYMMDD`. So a run with all of them gives:

```
Alex Morgan Taylor - Records Officer - Redgate Council - 20260902 - CV.pdf
```

and a run with only a role gives `Alex Morgan Taylor - Records Officer - 20260902 -
CV.pdf`, with no empty gap between two hyphens where the employer would have been.

**`--employer` is why it is there.** Two applications for the same job title, built from
the same markdown on the same day, otherwise produce one filename and the second run
writes over the first. Pass it whenever the employer is known, which is always by the
time a PDF is being printed.

Re-rendering the same skin replaces the file, which is what somebody trying six skins
wants. A different advertisement does not: the earlier PDF is moved aside under a dated
name first and the run says so.

### Why a browser and not a library

The PDF has to be the skin, not a second opinion about it.

- **A Python PDF library** (WeasyPrint, ReportLab, fpdf) is its own layout engine. It
  would re-flow the CV against its own font metrics, its own line breaking and its own
  idea of flexbox, and the answer would be close and wrong: a meter a millimetre
  short, a sidebar the wrong green, a role that falls onto page two. Close and wrong
  is worse than absent, because nobody proofreads a PDF they asked for.
- **A canvas snapshot** (html2canvas and the like) is a picture. The applicant
  tracking system that opens it first finds no text at all, the recruiter cannot copy
  an email address out of it, and the file is ten times the size.
- **The browser that already drew the preview** needs no reconciling. Same CSS, same
  `paginate.js`, same page breaks, and the glyphs come out as vector text.

`scripts/to_pdf.py` finds Chromium, Chrome, Edge or Brave: on `PATH`, then the usual
install locations on Windows, macOS and Linux, then a Playwright cache. `CV_BROWSER`
points at one directly. Nothing is installed and nothing is downloaded.

### The typeface check, and why it refuses

A browser that cannot load a webfont does not report an error. It substitutes a face
with different metrics and re-flows every line against it. The document still looks
finished. The page breaks have moved, the sidebar text wraps differently, and it is
not what was approved.

So after printing, `--pdf` reads the font names back out of the finished PDF and
compares them with the faces the skin asked for. If one is missing it deletes the
file and says which face and why. `--pdf-allow-substitute` writes it anyway, and is
for the case where a near miss is genuinely fine.

This check only means something because the typesets name real bundled families. When
they named Georgia and Helvetica Neue, no face resolved, nothing was embedded, and the
check short-circuited to "nothing missing" while the PDF came out in whatever the
machine had.

### Carrying the fonts

```bash
python3 scripts/fetch_fonts.py             # every family in assets/fonts.json
python3 scripts/fetch_fonts.py lora source-sans
```

This writes into `assets/fonts/`, and everything the skill ships with is already there.
The renderer embeds those files in the document as base64, which is the one mechanism
described under **The faces** above. A single variable file can go in by hand as
`<key>-variable.ttf` and is declared across the whole weight range rather than as two
fixed weights, so bold is real bold rather than a smear.

The renderer's matcher reads the whole folder rather than insisting on one filename, so
a family downloaded from Google's own zip drops straight in under whatever name it
arrived with.

### Pagination waits for the fonts

`paginate.js` measures text to decide where a sheet ends, so it waits for
`document.fonts.ready` before reading a single height. Measured in the fallback face
and repainted in the real one, every measurement is wrong by a little and a bullet
that fitted moves to the next page, and wrong differently in the preview than in the
print, which is exactly the drift this whole file exists to prevent. A font server
that never answers costs three seconds, not the document.

### The studio's Save as PDF button

The button tries the browser's own print first, which is the real thing and works
when the studio is open as its own page. Inside a preview frame a page is not allowed
to open a print dialog, and that failure is silent, so the button falls back to
copying the `--pdf` command for the exact skin on screen. Handing that to Claude
prints both documents where the files are.

It does not save the pages as HTML. That was the old fallback, and it left people
holding two files they still had to print themselves, which is the job they pressed
the button to avoid.

### Checking a print

Count the pages in the finished PDF rather than looking at a print preview. `--pdf`
prints the count it got. Check the colour by rendering page one to an image and
sampling a pixel inside the sidebar, because Save as PDF leaves background graphics off
by default in most browsers and `print-color-adjust:exact` inside `@media print` is the
instruction not to. Check the text by extracting it and reading it, because that is what
a screener gets. `references/ats.md` has that check and what has to be true in it.

**The trailing blank page.** `#doc` carries a 1px bottom padding on screen so the last
sheet's shadow is not clipped. In print that 1px is a whole extra sheet of paper, and it
came out of every printer until someone counted the pages in a PDF rather than looking
at the preview. `@media print` now zeroes `#doc` padding, margin and line-height, and
restores `line-height:normal` on the sheet.
