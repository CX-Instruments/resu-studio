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

Three things have to be true:

1. **The person's name is the first thing in the file**, whole, on one line.
2. **Every section heading appears as a word.** `EDUCATION`, not `E D U C AT I O N`.
   A screener uses those headings to decide where experience stops and education
   starts. A heading it cannot match is a section it may not record at all.
3. **Nothing is interleaved.** A paragraph should not have a phone number or a skills
   list threaded through the middle of it.

If any of those fail, say so and offer a different layout. Do not hand over a document
that has failed this check with a note attached; the person will not read the note.

## Tracking is in em, never in px

A fixed pixel gap between letters is proportionally much wider at 8pt than at 10pt.
Past a threshold the extractor decides the gap is a word space and writes one. That is
where `E D U C AT I O N` comes from, and it happened in every layout in this skill
until the stylesheet was changed to express tracking as a fraction of the font size.

Headings still look tracked. They just stop falling apart on the way into a screener.
**If you are editing the stylesheet, do not put pixel values back.**

## Two columns read out of order

A sidebar is a column of text beside another column of text. On the page a person
reads them as two panels. An extractor reads them as one stream, and what comes out
depends on where each line happens to sit.

Measured on the layouts in this skill:

| layout family | what the extractor gets |
|---|---|
| `band`, `slab`, `panel`, `spine`, `cards`, `rail`, `classic`, `compact`, `hairline`, `bands` | name first, whole, then every section in order |
| `sidebar-*` (all eight) | the name wraps mid-way, so it arrives as two lines |
| `sidebar-right`, `sidebar-tint-right`, `sidebar-top-right` | the file **opens with PROFILE**; the name arrives later, threaded through the profile paragraph |

None of this makes a sidebar wrong. A sidebar CV read by a person is often the better
document, and plenty of applications go straight to a human — a small employer, a
direct approach, a referral. But when the advertisement names a job board, a government or
large-employer portal, or any "upload your resume" form, a single column is the safer choice
and the person should be told why rather than quietly switched.

**Say it as a trade, not a rule.** "This one reads better on screen; this one survives
the upload. Which is it going for?" is a question they can answer. "Sidebars are bad
for ATS" is folklore they will find contradicted somewhere else within a day.

## Keywords, and the line this skill will not cross

A screener looks for the advertisement's own terms. Where the person has done the
thing and calls it something else, the fix is to use the employer's word for it —
that is `scoring.md`'s "say it in their words", and it is honest.

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
  not the drawing means anything to the reader.
- **Dates print as text** in the role heading, in the person's own format.
