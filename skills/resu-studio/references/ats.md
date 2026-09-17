# What the screener gets

Most applications are read twice: once by software that turns the PDF back into text
and tries to work out which part is experience and which is education, and once by a
person who spends well under a minute deciding whether to read it properly. The two
readers want different things and neither of them sees the page you designed.

This file is about the first reader. `voice.md` and `achievements.md` are about the
second.

## The check, and it is not optional

**Before handing over any PDF, extract the text and read it.** That is what a screener
gets, and it is the only way to know what it got.

```bash
pdftotext "path/to/CV.pdf" - | head -40
```

**Forty lines is a starting point.** On a right-hand sidebar the name arrives about two
thirds of the way down the file, well past line 40, so a check that reads only the head
reports a missing name that is in the file all along. Drop the `head` and read the whole
extraction the moment anything looks wrong:

```bash
pdftotext "path/to/CV.pdf" -
```

Three things have to be true:

1. **The person's name is present and unbroken.** Their whole name is in the file, in
   one run of characters, near the top. It may wrap onto two lines in a narrow column,
   and that is a cost rather than a failure: `FIRST MIDDLE` on one line and `LAST` on
   the next is still their name. What is a failure is the letters coming apart, so that
   the name arrives as `F IR ST MID DLE LA ST` and no search for it matches.
2. **Every section heading appears as a word.** `EDUCATION`, not `E D U C AT I O N`.
   A screener uses those headings to decide where experience stops and education
   starts. A heading it cannot match is a section it may not record at all.
3. **Nothing is interleaved.** A paragraph should not have a phone number or a skills
   list threaded through the middle of it, and a section heading should not land in the
   middle of another section's content.

**The check is run on the person's own file, every time.** Whether a name or a heading
survives extraction depends on the layout, on the tracking, on the point size, on how
long their name is and on how their own sections happen to fall, so a layout that came
through clean for the last person is not evidence about this one. The table further down
was measured on one CV and it tells you where to look. It does not stand in for the run.

## When the check fails, the person is told and the person decides

**Several layouts in this skill fail check 3, including the default one.** That is
measured and it is in the table below. A layout that interleaves is not a broken layout
and it is not a document to withhold. It is a document that reads one way on paper and
another way through a parser, and which of those matters depends entirely on where the
application is going.

So the finding goes to them, in their own file's words: what the extraction opens with,
which heading landed inside which block, where their skills ended up. Then the trade,
with a layout named that came through clean:

> Extracted, your CV on this skin opens with your name, then the KEY SKILLS heading
> lands between the two paragraphs of your profile, and your achievements arrive after
> education and training. On the page none of that is visible. A screening system reads
> the file in that order.
>
> `spine`, `rail` and `cards` came through with every section in one piece. They are the
> same content in a different shape. Is this one going to a person, or to an upload form?

**Do not switch the layout for them, and do not talk them out of the one they chose.**
Where the application reaches a person, an interleaved extraction costs nothing anybody
will ever see, and a good-looking page is worth something. Where it goes through a job
board, a government portal or any "upload your resume" form, it costs the reading order
of the whole file. Say which of those it is before they send it.

**What is not a trade is a heading that came apart.** `E D U C AT I O N` or
`TR AINING AND CERTIFICATIONS` gives a screener nothing to match on, and no reader
benefits from it either. When check 2 fails, say so and move them to a layout where it
passes.

## Tracking is in em, never in px

A fixed pixel gap between letters is proportionally much wider at 8pt than at 10pt.
Past a threshold the extractor decides the gap is a word space and writes one. That is
where `E D U C AT I O N` comes from, and it happened in every layout in this skill
until the stylesheet was changed to express tracking as a fraction of the font size.

Tracking is now `0.090em` throughout, so the gap no longer grows with the point size.
**It does not make the problem go away.** Tracked uppercase headings still come apart
in extraction on some layouts, and a heavily tracked name does too. That is what check 1
and check 2 are for, and it is why they are run on the real PDF rather than assumed.

**If you are editing the stylesheet, do not put pixel values back.**

## What the eighteen layouts actually extract as

A sidebar is a column of text beside another column of text. On the page a person
reads them as two panels. An extractor reads them as one stream, and what comes out
depends on where each line happens to sit.

Measured on 2 September 2026 against one real CV of two pages, printed in all eighteen
layouts on `--palette forest` at the default typeset, with the person's own decisions
file applied, and read back with `pdftotext`. The commands are at the foot of this
section.

The name came out whole in all eighteen. No layout broke it into letters on this file,
including `panel`, `classic` and `hairline`, whose tracked uppercase name is the one most
at risk of it.

| layout | what the extraction reads like |
|---|---|
| `spine`, `rail` | name whole and first, then every section as its heading followed by its own content, in order, with each role's dates beside its own heading. Nothing out of place. `spine` prints the dates in capitals and `rail` wraps a long date over two lines in its gutter, and both of those are true on the page as well |
| `cards`, `bands` | the same, except that the last role's dates line lands at the very end of the file, after training and certifications |
| `band`, `panel`, `hairline` | the same again, and a second date drifts: the middle role's dates land three or four lines into that role's own bullets |
| `compact` | every section in one piece, but the whole KEY SKILLS block comes before the profile, the name and the contact line arrive joined as one line, and the last role's dates land at the end of the file |
| `classic` | every section in one piece and each role's dates on its own heading line. **Fails check 2**: `TRAINING AND CERTIFICATIONS` came out as `TR AINING AND CERTIFICATIONS` |
| `slab` | **Fails checks 2 and 3.** The gutter heading runs into the neighbouring body line, so the file carries `PROFILE` followed straight away by the first words of the profile, `KEY SKILLS` followed by the first group label, and `EDUCATION` followed by the first words of the qualification line. `PROFESSIONAL EXPERIENCE` and `TRAINING AND CERTIFICATIONS` are each split over two lines, and the training heading has a body line inserted into the middle of it |
| `sidebar-dark`, `sidebar-tint`, `sidebar-line` | **Fails check 3.** Name first, wrapped over two lines, then the contact block. Then the profile's first paragraph, the KEY SKILLS heading, the profile's second paragraph, the first skills group label, the KEY ACHIEVEMENTS heading, the rest of the skills, education, training, and only after all of that the achievements themselves and the experience section |
| `sidebar-top` | **Fails check 3.** Name first, wrapped, then the whole sidebar, then the main column, with the two training entries threaded back through the middle of the experience section |
| `sidebar-right`, `sidebar-tint-right`, `sidebar-line-right` | **Fails check 3.** The file opens with PROFILE. The achievements print with no heading in front of them. The name and the contact block arrive about two thirds of the way down, after most of the experience section. The skills block is then split in two with role bullets between the halves, and the first role's dates land far above their own heading |
| `sidebar-top-right` | **Fails check 3.** Opens with PROFILE, name near the end, and the EDUCATION heading is separated from its one line by the whole PROFESSIONAL EXPERIENCE heading and its first role |

**All eight sidebar layouts interleave, not only the right-hand four.** The earlier
version of this table said the left-hand ones came out as name, then sidebar, then main
column. They do not. The two columns thread through each other, and the headings land
inside whichever block happens to be beside them.

**What the sides do change is where the name lands.** A left-hand sidebar carries the
name and is read early. A right-hand one carries the name and is read after the whole
main column, so the first thing a parser meets is the word PROFILE.

**The drifting dates line is worth naming when it happens.** On `cards`, `bands`, `band`,
`panel`, `hairline` and `compact` at least one role's dates left its heading, usually the
oldest role's, which ended up after training and certifications. A parser building an
employment history from that file can attach the wrong dates to a role, or none. It is a
smaller cost than an interleaved column and it is still a cost.

**Where a date drifts depends on how the CV happens to fall**, so this row of the table
is the one most likely to read differently for the next person. The layouts either side
of the drift did not change; which particular date left its heading did.

**A layout that fails is still a layout somebody may want.** A sidebar CV read by a
person is often the better document, and plenty of applications go straight to a human:
a small employer, a direct approach, a referral. The failure is only a failure at the
parser, so it is the destination that decides.

**The default layout is `sidebar-dark`, and it interleaves.** So on a default render the
check fails, and the person hears about it and picks. The layouts to offer are `spine`,
`rail`, `cards` and `bands`, which came through with every section in one piece on this
CV, and `spine` and `rail` also kept every date beside its own role. Then run the check
again on whatever they choose, because the table is a starting point rather than a
promise about their file.

Re-measure it like this, on their own file:

```bash
J="$(python3 scripts/paths.py --job <job id>)"
python3 scripts/render_cv.py "$J/cv-<variant>.md" --decisions "$J/cv-decisions.json" \
    --layout <the layout> --palette <their palette> \
    --job <job id> --pdf
pdftotext "$(python3 scripts/paths.py --job <job id> --job-documents)/<the finished>.pdf" -
```

To re-measure the whole table, loop the same two commands over the eighteen names that
`python3 scripts/render_cv.py --list` prints, writing each PDF to a folder of its own.

## Keywords, and the line this skill will not cross

A screener looks for the advertisement's own terms. Where the person has done the
thing and calls it something else, the fix is to use the employer's word for it. That
is `scoring.md`'s `buried` state and its "say it in their words", and it is honest.

Where they have not done the thing, there is no fix. A CV padded with terms the person
cannot speak to passes the software and fails the interview, and the person has to sit
in a room and account for a line they did not write.

**Never** add a keyword block, a "core competencies" list of bare nouns, white text, or
a term the record does not support. The bans in `voice.md` apply here without
exception.

## What is already safe, and does not need working around

- **The text is text.** The PDF is printed through a browser, so every character is a
  real character. It is not an image and it is not rasterised.
- **The skills graphics keep their words.** Bars, dots, rings and chips all print the
  level as text beside the drawing, so `A skill (Advanced, 10+ yrs)` extracts whether or
  not the drawing means anything to the reader. Checked by printing the same CV in each
  of the six treatments and extracting the text: the level is in the extraction every
  time, and under `bars`, `dots` and `rings` the legend naming the scale comes out too.
- **Dates print as text** in the role heading, in the person's own format.
