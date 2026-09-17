# The cover letter

One page. Never two. A cover letter that runs onto a second page is a cover letter
nobody finishes, and the reader was only ever going to give it ninety seconds.

It is written last, after the scoring, because it can only be written once you know
which of the person's evidence the advertisement actually wants.

---

## What it is for, and what it is not for

**The statement of claims answers the criteria. The CV lists the record. The letter
does the one thing neither of those can: it says why this person, for this job.**

So the letter must not be a summary of the CV in prose. If a paragraph could be
deleted and nothing would be lost that the CV does not already say, delete it. The
test for every paragraph: does a reader who has the CV in front of them learn
something from this?

What earns its place:

- the thread that runs through the career, which a reverse-chronological CV hides
- why this employer and this function, in terms specific enough that the letter
  could not be sent to anyone else
- the standard the person holds themselves to, shown rather than claimed
- one thing they would want to talk about, which invites the conversation

What does not:

- restating the profile
- listing skills that are already in the skills section
- "I am a highly motivated professional with excellent communication skills"
- any sentence that apologises, hedges, or explains a gap

## The shape

```
letterhead        the same name and contact block as the CV, from the same source
date              the day it is sent, not the day it was drafted
addressed to      role title, section and branch, agency, and the position number
salutation        to the named contact if the ad gives one, else the panel
body              four to six paragraphs
sign-off          and the name
```

**The letterhead is the CV's letterhead.** Same name, same contact lines, same
typeface, same skin. Two documents that arrive together and look like they came from
different people undo each other. The studio and the renderer both take the
letterhead from the CV file for exactly this reason, so the two cannot drift.

**Take the addressee from the advertisement, not from a template.** The section, the
team, the employer and any position or reference number are in the ad or its pack. Getting
the branch name wrong is the cheapest possible way to look like a mass application.

## Reading for both a screen and a person

Some applications are read by a person first, and a great many are filtered by
software first, and the two want different things. They are not in conflict here.

**For the screener:** the role title exactly as advertised, the position number, and
the terms the advertisement itself uses, appearing naturally in sentences. Plain
paragraphs, one column of text, no tables, no text boxes, no headers or footers
carrying content, no graphics carrying words. Every layout in this studio prints
the letter as ordinary paragraphs for this reason: even the sidebar skins put the body
in one plain flow and use the column only for the letterhead.

**For the person:** paragraphs short enough to look readable at a glance, a first
sentence that is not "I am writing to apply for", and specifics with names and numbers
in them. A reader decides whether to keep reading from the first two lines.

## The rules that do not bend

- **Every claim traces to the record.** The letter invents nothing the CV cannot
  support. If a sentence would surprise someone reading the CV, cut it.
- **No defensive sentences.** Not about gaps, not about a career break, not about
  missing a desirable. A letter that raises a doubt has raised it.
- **No verb promotion**, same as everywhere else.
- **The person's own voice.** Read it aloud. If they would not say it, rewrite it.
- **Name the contact only if the advertisement names them**, and spell it as the
  advertisement spells it.

## The shape, when there is no advertisement

A general resume has no job pack to address, and the letter is still worth having: it
is the page somebody attaches to a speculative application or hands to a recruiter.

So the studio always has a letter. Where there is no letter file, it shows a scaffold
of prompts, one per line, set in grey italic inside a dashed box. They are there to be
clicked, filled in or taken off, and they are the only thing on that page that is not
this person's own wording.

**A prompt never prints.** It does not appear in Final view, it is not in the PDF, and
it is not in the markdown the studio hands over. A letter that still says "Role title,
exactly as the advertisement writes it" has not been written, and Save as PDF says so
rather than printing a sheet of instructions with somebody's name at the bottom.

**A prompt stays a prompt until the person deals with it.** Not the AI. Filling the
letter in unasked is writing on somebody's behalf without being asked to, and it is the
one thing this scaffold must not invite. The letter is written in Phase 7, when they
ask for one.

## In the studio

The Skin tab has a Resume / Cover letter toggle. The letter wears whatever skin is
selected, and switching skin changes both documents together, because they are meant
to be posted together.

Every line of the letter can be pointed at exactly like a line on the CV: flag it,
ask for a rewrite, put it in your own words, take it off this version, or add a
paragraph after it. Nothing touches the markdown.

**Write the letter** at the top of the page opens one box for the whole thing. Paste a
letter already written, or type one, with a blank line between paragraphs. It is read
by shape and not by markup, the same way `parse_letter` reads the file, so a date, an
address block, a `RE:` line, a `Dear ...` line and a sign-off each land in their own
place. Anything not in the paste stays a prompt. Six paragraphs through six separate
little editors is not writing, which is what that box is for.

**What the person writes there stays.** It is saved against that application in their
browser and it survives a rebuild. A rebuild that brings a written letter file with it
does not replace what they wrote: a banner at the top of the page says the other letter
arrived and offers it, and the choice is theirs.

**The subject line has an id of its own.** `cover-letter/re` sits above the salutation
and carries the role title as the advertisement writes it, which is the first thing a
screener matches on. It prints in the body and not in the address block, so a sidebar
skin cannot put it down the side of the page in eight point.

**The studio hands the letter back as markdown.** Copy settings and Save as PDF both
write the finished letter out under the render command, to be saved as
`cover-letter-<variant>.md` and printed from. The markdown stays the master, and the
page and the print keep one reader between them.

`render_cv.py --letter <file.md>` renders the same thing from the markdown, on the
same skin, taking the name and contact block from the CV file.

**The same skin means the same layout, the same palette and the same typeset**, copied
off whatever the person landed on for the CV in Phase 6. The two files are opened within
a minute of each other by the same reader, so a letter in a different colour reads as
somebody else's letter, or as a template the applicant did not look at. One command with
both `--letter` and the skin flags on it writes both PDFs, which is the way to be sure
they cannot end up on different skins by being printed at different moments.

**They are saved separately.** Save as PDF at the top gives one file per document, each
in Final so nothing but the document reaches the paper. They are two documents and a
panel reads them as two.

**The markdown is the master.** The letter file is plain: blocks separated by blank
lines, in the order above. The renderer reads it by shape rather than by markup, so
nobody has to learn a format to write a letter.
