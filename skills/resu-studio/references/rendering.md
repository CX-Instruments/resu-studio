# Rendering

Two renderers, both optional, both last. Neither can change what a document says.

```bash
python3 scripts/render_cv.py cv-data-reporting.md --layout sidebar-dark --palette forest
python3 scripts/render_cv.py cv-data-reporting.md --gallery --outdir skins-samples
python3 scripts/render_cv.py --list
python3 scripts/render_report.py scorecard-after.md --before scorecard-before.md
```

## Do not choose a skin by reading this file

There is a studio. It draws the person's own CV live, on a phone or a laptop, with
every layout, palette, typeface, skills treatment, section order and column placement
as a control, and it prints the exact command line for whatever they land on. Send them
there and render what they choose. Guessing on their behalf and showing them one render
is how the last version of this wasted an evening.

The studio is an HTML page holding the CV as data. Rebuild it from the current CV when
the wording changes, publish it, and give them the link.

## The faces

`assets/fonts.json` holds the twenty-one faces a CV can be set in. Headings and body
text are chosen separately:

```bash
--head-font oswald --body-font work-sans --size normal
```

Eighteen come from Google Fonts and are fetched by the rendered page itself, which adds
a `<link>` for **only the two families that page is actually set in**. Arial, Times New
Roman and Verdana are already on every machine and fetch nothing. A page rendered with
a Google face needs the network the first time it is opened; the fallbacks in each
stack keep it readable offline.

`--size small|normal|large` scales the whole document by 0.94, 1 or 1.06. The old
`--typeset` pairs still work and still set both faces at once; `--head-font` and
`--body-font` override them.

**In the studio every face is labelled in itself.** A list of font names set in one font
tells you nothing, which is the whole reason for showing them this way.

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
heading. On a single-column layout the flag is accepted and ignored, because there is
nowhere to send anything.

`--hide-groups "Domain;AI and emerging tools"` leaves named groups off this version,
matched on their exact headings. **It is never silent.** The run prints what it took off
and how many skills went with it, says that the line count above it is the parse rather
than what printed, and warns on stderr if a heading was named that no group has. Use it
for a version of the CV, not for tidying: a group that is wrong belongs out of the
markdown.

`--gap tight|normal|airy` sets the space between groups. `--no-legend` drops the line
that says what the five steps are, which should only be dropped when no group is drawn
on a scale.

### The rule the drawings are built on

**A bar, a dot or a ring is drawn only where the markdown states a level.** There is no
default level, no inferred level and no average. Skills with no stated level print as a
line of text under the graphic, in their own words, so nothing is lost and no number
appears on the page that its owner did not put there. Anything in brackets that is not
a level, "10+ yrs", "personal development projects", travels with the skill.

## Section order and which column

`--order` takes the section headings as slugs, in the order they should print, each
optionally with `:side` to send it to the sidebar:

```
--order profile,key-skills:side,professional-experience,education,training-certifications
```

`:side` only does anything on a layout that has a sidebar. A section the flag forgets
still prints, last, in the main column, and the run says so. **The renderer never drops
a section.** Taking something off the page is an edit to the markdown, never a flag,
for the same reason the line count is enforced.

`--group own|discipline|strength` regroups the skills without rewording them. `own`
keeps the headings as written. `strength` regroups by the level each skill states.
`discipline` reads `assets/regroup.json`, which maps new headings to the ones in the
markdown; with no such file it falls back to `own` and says so.

## The contract, and how it is enforced rather than promised

**Reads the markdown and nothing else.** No ledger, no notes, no proposals file. The
old workflow rendered from the history files, which is how a reviewer's working notes
printed on a finished CV. The renderer cannot reach them because it never opens them.

**Adds nothing, drops nothing.** `render_cv.py` counts the content lines in the source
and the source lines the parsed document accounts for. **If the two differ it refuses
to write the file** and says so. Not a warning, not a note in the output, a refusal.
Every run prints the pair, for example "78 content lines in, 78 out".

**Never clips.** No fixed heights, no `overflow:hidden`, no absolute positioning
anywhere in the CSS. Long content makes the document taller. This is structural, not a
setting: a skills column with fifty lines produces a longer page, never a shorter one
with the end missing. Verified by measuring every element in a headless browser and
confirming no element has content taller than its box.

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

**It counts itself.** Before laying out it counts the blocks it is about to place, and
after laying out it counts what is on the sheets. If the two differ it throws the
pagination away and prints everything on one long sheet rather than showing a tidy page
with a line missing. Regions are `overflow:hidden` only while pagination is running, so
nothing can hide behind a page edge; there are no scrollbars inside the document, in
either direction.

Sheets sit on a grey ground with a gutter between them on screen, and `break-after:page`
sends each one to its own sheet when printed.

## Page count

The renderer does not enforce a page limit and does not try. It cannot know the
reader's paper size or margins, and a renderer that trims to fit is a renderer that
edits. Open the HTML and use the browser's print preview: it gives the true page count
and saves the PDF.

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
| `spine` | timeline down the left with a dot per role |
| `cards` | each role in its own tinted card |
| `classic` | centred, ruled, conservative |
| `compact` | two-up header, tighter leading, skills in two columns |
| `rail` | dates and section headings in a left gutter |
| `bands` | each section heading a full-bleed tint band |
| `hairline` | wide margins, thin rules, quiet |
| `panel` | the header inside a ruled box, headings with an accent bar |

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

| Layout | Shape |
|---|---|
| `plain` | One column, no rules |
| `rule` | One column, a coloured rule under each heading |
| `band` | Coloured header band, then one column |
| `aside-left` | Skills, education and certifications beside the profile, then experience full width |
| `aside-right` | The same, mirrored |
| `bandaside` | Header band plus the aside arrangement |
| `compact` | One column, tighter type, for fitting more |

Palettes: ink, forest, navy, slate, oxblood, teal, plum, sand, copper, mono.
Typesets: serif, sans, mixed (serif headings), mixedalt (sans headings), tight.

**`--gallery` renders the person's own CV in every layout and palette on one page**,
scaled down, so the choice is made by looking rather than by reading names. Pick one,
then render it properly.

**Which sections go in the aside** is decided by section title: key skills, skills,
education, training and certifications, certifications, eligibility. Everything else
flows below at full width. Rename a section in the markdown and it moves.

**A note on the aside layouts.** The aside sits beside the profile, and the row is as
tall as whichever column is taller. A long skills column beside a short profile leaves
white space to the right of the profile. That is the honest trade for never clipping:
the alternative is a fixed-height column, which is exactly the bug this replaces. If
the white space bothers you, `plain`, `rule` and `band` have none.

## The report

`render_report.py` reads `scorecard.md` and draws:

- **Two gauges.** What you have, measured against the facts ledger. What a reader
  would find, measured against the page as it stands. They are separate because they
  are different questions, and showing one number instead of two is the mistake this
  workflow exists to avoid.
- **The gap between them** in one sentence, which is the case for doing the work.
- **A bar for each state**, with "not yet worked out" drawn separately from "do not
  have", because one means nobody has checked and the other means the answer is no.
- **The ask by ask table**, with evidence ids, so any row can be traced.

`--before <earlier scorecard>` puts a hollow marker on each gauge showing where it
stood before the person's decisions. That is the movement, and it is the honest way to
show it: the left gauge barely moves, because rewriting does not change what somebody
has done. The right gauge is the one that moves.

The report computes nothing of its own. It reports the numbers in the scorecard, and
if the counts are missing it derives them from the table and says so by showing the
same numbers back.

## If you use a different renderer

Fine, as long as it honours the contract above. If it cannot, prefer the markdown. A
CV the person can paste into anything beats a designed one that quietly disagrees with
its own source, and this workflow has already produced one of those.

## Sections the person added

`--decisions` also carries sections that are not in the markdown. The studio writes
them into `cv-decisions.json` under `sections`:

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
missing it throws the pagination away and prints the whole CV on one long sheet, because
a visibly long page is a problem someone can see and a silently dropped line is not.

## Absolute gutters need a width the content fits

`rail` and `spine` hang dates and headings in the margin with `position:absolute` and a
fixed width. A date longer than that width does not wrap by default, because
`.roledates` is `white-space:nowrap` in the base: it overflows to the right and prints
on top of the role title. "Aug 2022 to May 2023" is 111px at 8pt; the gutter was 79px.
Any layout putting text in a fixed-width gutter has to set `white-space:normal` and a
width the longest real value fits, and be checked against a date range rather than a
bare year pair.


## The sidebar that is only on page one

`sidebar-top` and `sidebar-top-right` put the sidebar on the first sheet and nowhere
else. That is the layout, not a bug: the skills column earns its place beside the
profile, and by page two the reader is in the roles and the width is worth more than
the panel. The following sheets keep an 8mm tint edge so they still read as the same
document.

**What was a bug is the hole it used to leave.** When the sidebar ran out of content
part-way down page one, the rest of that page stayed in a narrow column beside an empty
tinted panel.

**The fix is a float, not a second region.** The panel is a floated block inside page
one's own text flow, so the text runs beside it and then wraps underneath it with no
break and no hole. The first attempt used a separate region below the grid, and it was
worse than the problem: the column above stopped wherever its last whole block fitted,
so a bullet appeared alone at the foot of the page with a hand's width of white above
it. A column break is a hole with extra steps. Let the text wrap.

Two things the float needs. The panel must size to its own content, so `.aside.float`
overrides the `height:100%` that stretches a grid column. And it has no height of its
own to measure against while it is being filled, so `fill` takes a gauge element: the
sheet region, which has a fixed height and `overflow:hidden`, and therefore contains the
float and says truthfully when the page is full.

Its width comes from the page, `calc(35% + 13mm)` against the region's own padding, not
a figure in millimetres, so it holds if the paper changes.

## Two columns for a flat list

`--columns education,training-certifications` runs those sections in two columns. Only
flat lists take it: a set of short lines, one per item. A paragraph cannot, roles cannot,
and skills has its own treatment.

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

## Sidebar, page one

Page one has a sidebar, floor to ceiling, 35% of the width. Page two onwards does not.
That is the whole of the layout and there is nothing conditional about it: the column is
there whether its content fills it or not, exactly like the full-height sidebars, and it
simply stops after page one. Later sheets carry an 8mm tint edge so they read as the
same document.

If the sidebar cannot hold everything on page one, the remainder joins the main flow at
the top of page two with its heading cloned onto it, so it arrives as a headed section
rather than a run of orphan blocks.

**Two attempts at being clever here were both worse than the plain thing.** Cutting the
panel to the height of its content and flowing the rest of page one underneath produced
a column break, and a column break strands a bullet at the foot of the page. Making it a
float fixed the break but meant the panel stopped wherever its content did, which reads
as a sidebar that got cut off. Trying the panel whole and falling back to a name plate
avoided both and gave a layout called "sidebar, page one" with no sidebar on it. The
column is a column. Leave it alone.

## Two columns for a flat list

`--columns education,training-certifications` runs those sections in two columns. Only
flat lists take it: a set of short lines, one per item. A paragraph cannot, roles cannot,
and skills has its own treatment.

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

## Group the studio by what the layout does

Eighteen layouts in one long list is a wall. They sort into four families by the shape
of the page rather than by name, and each family gets a plain-English line: a column
beside the page, a block across the top, something down the side of the roles, nothing
but type. Pairs that differ only in which hand they sit on stay next to each other, so
`Sidebar, page one` and `Sidebar, page one, right` are side by side rather than three
rows apart.

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

## Save as PDF

One button, at the top. It prints each document in turn, straight from the studio page,
and the browser's own Save as PDF writes the file. The browser's own print, from the
menu or the keyboard, does the same thing: whichever way a print starts, what comes out
is the sheets.

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

**When the browser will not print at all,** the studio saves each document as a
standalone page that opens its own print dialog. Below that there is a third route which
is the most reliable of the three: Copy settings on the Working tab, handed to Claude,
who runs `render_cv.py` and writes both PDFs into the person's folder.

## PDFs rendered outside the browser

Claude can produce the finished PDFs directly, which is what to do when the person's
browser is fighting the print dialog or they simply want the files.

    python resu-studio/scripts/render_cv.py "<cv>.md" --layout ... --palette ... \
        --head-font ... --body-font ... --size ...          -> the CV page
    same, plus --letter "<cover letter>.md"                  -> the letter page

then print each page to A4 with a headless browser, zero margins, backgrounds on.

**The faces have to be installed, not fetched.** `fonts.googleapis.com` is not reachable
from the places this runs. The same families are in the `google/fonts` repository, which
is, so clone it sparsely for the families in `assets/fonts.json` and install them.

**Install static instances, not the variable files.** A variable font makes Chromium
write every glyph as a Type 3 drawing procedure, and some keyword screeners cannot pull
text out of that. `fontTools.varLib.instancer` pins each family at weight 400 and 700 and
writes plain static faces; the PDF then carries CID TrueType subsets, which read cleanly.
Check with `pdffonts`: the type column should say TrueType, not Type 3.

**Name the files for the person, the role and the date**, because that is what a panel
sees in a folder of applications:

    <full name> - <role> - <date> - CV.pdf
    <full name> - <role> - <date> - Cover letter.pdf

**The trailing blank page.** `#doc` carries a 1px bottom padding on screen so the last
sheet's shadow is not clipped. In print that 1px is a whole extra sheet of paper, and it
came out of every printer until someone counted the pages in a PDF rather than looking
at the preview. `@media print` now zeroes `#doc` padding, margin and line-height, and
restores `line-height:normal` on the sheet.

**Colour has to be forced.** Save as PDF leaves background graphics off by default in
most browsers, which prints a dark sidebar as white paper and a tinted panel as nothing.
`print-color-adjust:exact` on everything, inside `@media print`, is the instruction not
to. Without it the skin the person chose is not the skin that arrives.

**Check prints by counting pages in a real PDF**, not by eye in a print preview. Render
the page headless, print to A4 with zero margins, and count the pages in the file. All
eighteen layouts, both documents, print exactly the number of sheets the studio says they
will. Check the colour the same way: render page one of the PDF to an image with
background graphics off, and sample a pixel inside the sidebar. Check the text the same
way: extract it and read it, because that is what a screener gets.

---

## Printing to PDF

`--pdf` is the last step. It writes the HTML exactly as it always did, then hands
that file to a real browser and asks the browser to print it.

```bash
python3 scripts/render_cv.py cv.md --letter cover-letter.md \
    --layout sidebar-dark --palette forest --pdf
python3 scripts/render_cv.py cv.md --pdf --pdf-dir "<the folder they asked for>"
```

One run writes every document it was given: `<Name> - Resume.pdf` and
`<Name> - Cover letter.pdf`. They are posted together, so they are printed together.

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

### Carrying the fonts, so the check always passes

```bash
python3 scripts/fetch_fonts.py             # every family in assets/fonts.json
python3 scripts/fetch_fonts.py lora source-sans
```

This writes `assets/fonts/<key>-400.woff2` and `-700.woff2`. From then on the
renderer embeds those files in the document as base64, and the page draws the same
letters on a machine with no network at all, which is where PDFs usually get made.
A single variable file can go in by hand as `<key>-variable.ttf` and is declared
across the whole weight range rather than as two fixed weights, so bold is real bold
rather than a smear.

Faces with no `g` entry in `fonts.json` — Arial, Times New Roman, Verdana — are the
machine's own and are never fetched. They are also the one case where the file
depends on what is installed, so a skin built on them prints exactly only where those
faces exist.

### Pagination waits for the fonts

`paginate.js` measures text to decide where a sheet ends, so it waits for
`document.fonts.ready` before reading a single height. Measured in the fallback face
and repainted in the real one, every measurement is wrong by a little and a bullet
that fitted moves to the next page — and wrong differently in the preview than in the
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
