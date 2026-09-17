# Phases 6 and 7 in full: assemble, rescore, design, print and the letter

SKILL.md carries the short version of these phases. This is the whole of them, with
every reason behind each rule. Read Phase 6 here before running `assemble.py`, the
design and PDF sections before any render, and Phase 7 before writing the letter.

## Phase 6 in full: Assemble and rescore

**`scripts/assemble.py` writes the assembled CV.** It reads the CV the studio was built
from and the decisions file the person saved, and writes `cv-<variant>.md` holding
everything they decided: every rewrite in their own wording, every line they took off
actually gone, every line they added in the place they added it, every list in the order
they put it in, and every extra section they ticked written in as a real section.
Anything nobody decided about is copied through byte for byte, so assembling with an
empty decisions file gives back the file it was handed, unchanged. The markdown file is
the deliverable and the master, and this is the command that makes that true.

```bash
D="$(python3 scripts/paths.py --data)"
python3 scripts/assemble.py "$(python3 scripts/paths.py --cv-source)/<their CV>.md" \
    --decisions "$D/cv-decisions.json" \
    --out "$D/cv-<variant>.md"
```

The first argument is the same markdown Phase 3 and Phase 4 passed as `--cv`, because
every decision in the file was made against that document. `--out` is required and it
refuses to write over the source. `--archive` defaults to `cv-<variant>-archive.md`
beside `--out`, and `--variant` is read off the `--out` filename. Exit 0 means it wrote,
1 means it refused and said the reason, 2 means the command line was wrong.

**Read what it prints, and tell them what is in it.** It names every rewrite, every line
taken off with its id and its wording, every line added, every list reordered and every
section written in. That is the account of what changed, and it is the only place the
account is given now: the render has nothing left to apply, so it reports none of this.

**The archive is `cv-<variant>-archive.md`, beside the CV.** Every line taken off is in
it in full, with its id, its wording, the reason and the date, and every rewrite is in it
with the wording before and the wording after. It is appended to on each pass and nothing
in it is ever rewritten. It is the durable record of what came off, so a person who wants
a line back has a file to open.

**The last line of the assembled file is one HTML comment saying which decisions are
baked in.** It never prints and it is not counted. Leave it exactly as it is: it is what
stops the same decisions being applied a second time.

**Close the proposals out before assembling.** Line ids are positional, so once the file
is assembled every id names a line of the assembled document. A proposal, a note or a
hand-to-AI line still carrying a pre-assembly id points at the wrong line, and a
proposal for a line they took off names nothing at all. Record every decision against its
proposal first. Anything they want to change after this belongs in the new studio the
rebuild below gives them.

Then rescore: keep the first `scorecard.md` as `scorecard-before.md`, write the new
one against the assembled CV, and rebuild the studio from it with the assembled CV as
`--cv`. Same `--role` and same `--employer`, for the reason given under *Rebuild the
studio every time the page changes* in SKILL.md and `references/studio.md`, so it is written under the same filename and
their marks, which are keyed to that role and employer, are all still there. The
Score tab they have been reading all along now shows the new numbers, and they watch
it move rather than being told it moved.

**The rebuilt studio says the CV changed, and that is right after an assembly.** It is
reading a CV that is no longer the one their marks were made on, so it says on the page
what carried over, what it put back by matching their wording, and what it dropped
because the line it was made on has gone. Nothing has gone wrong. Say that plainly if
they ask about it, and do not go hunting for a fault.

**Pass the ledgers on this rebuild too.** A rebuild given only `--cv`, `--role` and
`--employer` opens with an empty Score tab, no suggestions and no achievements panel,
and prints `asks : 0 (not scored yet)` while you are telling them to watch the score
move.

```bash
D="$(python3 scripts/paths.py --data)"
python3 scripts/build_studio.py --cv "$D/cv-<variant>.md" \
    --scorecard "$D/scorecard.md" --asks-md "$D/asks.md" \
    --facts "$(python3 scripts/paths.py --facts)" \
    --proposals "$D/proposals.md" --achievements "$D/achievements.md" \
    --role "<the job title>" --employer "<the employer>" \
    --letter "$D/cover-letter-<variant>.md"
```

Drop `--letter` on the first pass through Phase 6. It goes in when a letter already
exists from an earlier run, and otherwise the letter arrives in Phase 7 and this is
built again then.

Then run the check. It now reads the assembled markdown against the decisions file
beside it and names anything the two disagree about: a line the decisions take off that
is still in the file, a line the person added that is missing from it, a rewrite the file
has not taken, a ticked section that is not there.

```bash
python3 scripts/check.py
```

Full instructions: `references/assembling.md`.

**Done when** every one of these is true:

- `assemble.py` exited 0 and named the file it wrote.
- `cv-<variant>.md` is in the person's folder, and so is `cv-<variant>-archive.md`
  whenever the run baked anything in at all.
- What it printed accounts for the decisions file: every rewrite, every removal, every
  addition, every reorder and every ticked section is on that list, and anything it
  reported as having no line to land on has been read and dealt with.
- `python3 scripts/check.py` has been run and everything it named has been fixed or
  answered.
- The rescore is shown beside the first score so the movement is visible, and any ask
  that did not move is said out loud rather than left for them to notice.

**Design is a separate, optional step, and it renders the markdown.** It never reads
the ledgers, never invents a line, and never truncates. It dresses both documents: the
resume and the letter always wear the same skin.

**Do not pick the design for them.** They already have the studio from Phase 4, and the
rebuild above is the page they are dressing. Let them choose. It draws their own CV
live with every layout, palette, typeface, skills treatment, section order and column
placement as a control, works on a phone, marks where A4 actually cuts, and prints the
command line for whatever they land on.

It writes into their documents folder, beside their finished PDFs. **Always pass
`--role` and `--employer`.** `--role` is required and the build refuses without it.
Together they name the file, key the studio's own browser storage so one application
cannot show another's marks, and tell two applications apart when a document would
otherwise be written over.

**The studio is built, never edited.** Editing the template by hand is what made a
second advertisement destroy the first, because there was only ever one copy. Building
the studio again for the same role, employer and CV file replaces that application's
own page. Anything else, including this rebuild, which reads the assembled CV rather
than the one from Phase 3, keeps the earlier page under a dated name and says where it
went.

Then render that.

**Every render still carries `--decisions` once a decisions file exists**, including the
gallery, including the HTML preview, and including the `--pdf` run. On an assembled CV it
applies nothing: `render_cv.py` reads the note at the foot, sees that these decisions are
already in the file, and says so in one sentence. Keep passing it anyway, because the
person can make new decisions in a studio built from the assembled CV, and those are
relative to the assembled document and do apply.

**Two things can still go wrong here, and neither of them is the assembled file.** The
first is a markdown nobody assembled: one written by hand, or the CV as it arrived. It
carries no note, so a render of it without `--decisions` prints the markdown alone, and
every line they took off comes back, every line they added is missing, every reorder is
undone and any section they ticked is not there, while the file still says "31 content
lines in, 31 out". The second is a decisions file changed after it was baked in. The note
records what was baked by what it does to the page, so a file that would now do something
different no longer matches it, and its additions print twice and its reordered lists
shuffle a second time. The render says that on stderr, and the answer is to assemble
again from the source rather than to patch either file by hand.

```bash
D="$(python3 scripts/paths.py --data)"
python3 scripts/render_cv.py "$D/cv-<variant>.md" --decisions "$D/cv-decisions.json" --gallery
python3 scripts/render_cv.py "$D/cv-<variant>.md" --decisions "$D/cv-decisions.json" \
    --layout sidebar-dark --palette forest \
    --role "<the job title>" --employer "<the employer>" \
    --skills list --skills-by "Technical=bars;Tools=chips" \
    --skills-order "Tools;Technical" --skills-place "Tools=main" \
    --gap normal \
    --order profile,key-achievements,key-skills:side,professional-experience,education,training-and-certifications
```

If no decisions file exists, because the person handed their work back as the pasted
block instead, drop the flag and say so out loud in the same breath: the render is then
the markdown, and the markdown has to already carry everything they decided.

The names in `--order`, `--skills-by`, `--skills-order`, `--skills-place` and
`--hide-groups` are this person's own headings, so read them off their markdown rather
than copying the ones above. A section `--order` does not name still prints, last, in
the main column, and the render says which. Any heading with the word "skill" in it is
the skills section, whatever else it is called.

**A section the person ticked is written into the assembled markdown, so `--order` names
it by its slug like any other section.** Key achievements comes through as
`key-achievements`. Read the order off the assembled file rather than off the CV as it
arrived, because that is where the section now is. A section `--order` leaves out prints
last in the main column and the run says so, which is almost never where a person wanted
their achievements.

The gallery draws one page per layout and palette, 180 of them, at the typeset it was
given. There are 900 skins in all: 18 layouts, 10 palettes and 5 typesets. The five
typesets are set in bundled families rather than in whatever the machine happens to
have: Lora throughout, Arimo throughout, Lora headings over Source Sans 3, Source Sans
3 headings over Lora, and Work Sans throughout at a slightly smaller size.

**The PDF is printed, not redrawn.** `--pdf` puts the finished HTML through a real
browser and writes both documents, one file each, on whatever skin was chosen. Same
CSS, same palette variables, same paginate.js deciding the page breaks, so the file
is the studio's own page: the colours, the layout, the meters and rings, the
typefaces. The text stays text, which is what an applicant tracking system reads.

```bash
D="$(python3 scripts/paths.py --data)"
python3 scripts/render_cv.py "$D/cv-<variant>.md" --letter "$D/cover-letter-<variant>.md" \
    --decisions "$D/cv-decisions.json" \
    --layout sidebar-dark --palette forest --head-font lora --body-font source-sans \
    --role "<the job title>" --employer "<the employer>" --pdf
```

**A `--letter` run does not rewrite the CV's own HTML file.** It writes both PDFs and the
letter's HTML, and the CV's named HTML is left exactly as the previous run made it. So a
CV HTML written earlier without `--decisions` survives beside a correct PDF, with the
deleted bullet still in it, and it is the file with the plain name that a person opens.
Two ways out, and take one of them: run the CV on its own with `--decisions` first so
that file is right, or delete the stale HTML and hand over the PDF alone. Never leave
two files in their folder that disagree with each other.

**The filename is what stops one application writing over another.** With `--role` and
`--employer` the PDFs are written as
`<Name> - <Role> - <Employer> - <YYYYMMDD> - CV.pdf` and
`<Name> - <Role> - <Employer> - <YYYYMMDD> - Cover Letter.pdf`, in that order, and a
segment with nothing in it is left out rather than printed as a gap between two
hyphens. Without `--employer`, two applications for the same job title built on the
same day produce one filename. `--date` writes the stamp however you pass it and
defaults to today as YYYYMMDD. `--out` names the HTML file, and `--pdf-dir` names the
folder the PDFs go to.

**Then read the PDF back as a screener would.** Most applications are parsed by
software before a person sees them, and what it receives is not the page you designed.
Extract the text and check three things: the name is first and whole, every section
heading appears as a word rather than spaced-out letters, and nothing is interleaved.

```bash
pdftotext "$(python3 scripts/paths.py --documents)/<the finished>.pdf" - | head -40
```

Drop the `head -40` and read the whole extraction the moment anything looks wrong. On a
right-hand sidebar the name arrives about two thirds of the way down, past line 40, so a
check that reads only the head reports a missing name that is in the file.

**All eight sidebar layouts interleave the two columns once extracted, and that includes
the default, `sidebar-dark`.** The measured read-back of a real CV puts the KEY SKILLS
heading between the two paragraphs of the profile and the KEY ACHIEVEMENTS heading inside
the skills block. On the four right-hand ones the file also opens with the profile and the
name arrives after most of the main column. `references/ats.md` carries the measured table
for all eighteen layouts and names the ones that came through with every section in one
piece.

So the check will fail on a default render, and when it does the person is told what the
extraction looks like and offered a layout that came through clean. An interleaved file is
fine for an application going to a person and a poor bet for one going through a job board
or a government portal. **Offer the trade rather than switching quietly, and rather than
withholding the document.** They choose where it is going, so they choose the layout.

Full instructions: `references/ats.md`.

**It refuses rather than guessing.** A browser that cannot reach a typeface does not
fail: it substitutes a face with different metrics, re-flows every line against it,
and writes a document that looks finished and is not the one that was approved. So
`--pdf` reads the faces back out of the finished file, and when one is missing it
deletes the PDF and says which. `python3 scripts/fetch_fonts.py` puts the font files
in `assets/fonts/` once, the renderer carries them inside the document from then on,
and the question never comes up again on any machine, with or without a network.
`--pdf-allow-substitute` overrides it, and should be rare.

**When the person pastes a command from the studio, read what came with it.**
Save as PDF hands over the command and, underneath it, the decisions as JSON: the
lines they took off this version, the ones they rewrote in their own words, the ones
they added, and any section that is not in the markdown. Write that JSON to
`cv-decisions.json` beside the CV markdown before running the command, which already
carries `--decisions`.

Write it down even when the CV has already been assembled, because it is the record of
what they decided and `check.py` reads it against the assembled file. If the command is
pasted before the assembly, the CV it names is the one that has not been assembled yet,
and skipping the JSON there is wrong in the worst way: the render prints from the
markdown alone, so every line they deleted comes back and every rewrite reverts, and the
PDF looks finished. They will not check a document they asked you to produce. **Final**
is the right-hand half of the Working and Final switch beside the zoom, and what it shows
is what they approved. The PDF has to match it.

The decisions file also carries an `order` key, so a bullet the person moved with the
arrows in the studio prints where they put it. The render lists every list it
reordered, with the original line numbers in their new order, and every line still
prints: one the order did not name keeps its own place at the end. A decisions file
that is not valid JSON, or whose order names a line twice or names one that is not
there, refuses in plain words and writes nothing, rather than printing a document
nobody can tell is wrong.

**Where they go.** `_Your Documents Are Here/` inside the person's own folder, which
is `python3 scripts/paths.py --documents`, or wherever `--pdf-dir` says. Put them in
the chat as well: a file they cannot find is a file they do not have.

A section that is a flat list of short lines can run in two columns, in the studio or
with `--columns`. Each skills group can be drawn its own way, and one treatment applied
to all of them looks lazy. Each group also has an order, a column and a show or hide of its own: groups
can be reordered against each other, sent individually to the sidebar or the main
column so the skills section spans both, and left off a version without touching the
markdown. Hiding says which groups it took off and how many skills went with them,
because nothing here disappears quietly. A bar, a dot or a ring appears only where the markdown states a level;
everything else prints as text, so no number reaches the page that its owner did not
write. `--order` moves sections and sends them to the sidebar, and never drops one.

**A CV can grow a section.** The studio holds six: profile, key skills, experience,
education, training and key achievements. Three of those can be added to a CV that
does not have them, and they are key achievements, professional memberships, and
volunteering and community. Until the assembly a ticked section lives in the decisions
file and prints on that version only. The assembly writes it into `cv-<variant>.md` as a
real section, which is the point of assembling. Key achievements is the
one you draft: six candidate lines out of their record worked against this
advertisement, each naming the ask it answers and the roles it rests on, and they tick
four to six of them. **Write them at career level.** Each line reaches across more than
one employer, so it says
something no role bullet says and nothing has to come off the page for it. A line that
restates a single bullet gets rewritten wider; the bullet is never deleted, because
that would leave the achievement with no job behind it.
`references/achievements.md`.

**Every line on the page can be pointed at.** Flag it, ask for a rewrite, put it in
their own words, take it off this version, or add one after it. Two queues on the edge
of the page keep score: what they have not decided about yet, and what they have handed
to you. Marking touches no file at all until Phase 6, and the assembly then writes every
line taken off into `cv-<variant>-archive.md` in full before it leaves the CV.
`references/marking.md`.

`render_cv.py` counts content lines in and lines accounted for, and refuses to write
the file if they differ. The rescore goes into the studio the same way the first score
did: rewrite `scorecard.md` and rebuild, so the Score tab moves and they watch it
move. Contract, skins, the skills treatments and the page count question:
`references/rendering.md`.

## Phase 7 in full: The cover letter

**Written last.** A letter written before the scoring is a letter about the person in
general. A letter written after it knows which of their evidence this advertisement
actually wants.

`cover-letter-<variant>.md`, in the person's folder. One page. Four to six paragraphs. It does the one job the
CV and the statement of claims cannot: why this person, for this job. If a paragraph
could be cut and nothing would be lost that the CV already says, cut it.

The letterhead is the CV's letterhead, taken from the same file so the two cannot
drift. The addressee, the position number and the contact's name come out of the job
pack, not a template.

Full instructions, including what earns a paragraph and what a keyword screener needs
from it: `references/cover-letter.md`.

**Print it on the skin the CV is already on.** The layout, the palette and the typeset in
this command are whatever the person landed on in Phase 6, copied across unchanged. The
two documents are posted together and are read within a minute of each other, so a letter
in a different palette reads as somebody else's letter. `--palette forest` here is the
Phase 6 example carried over, and it changes to whatever they actually chose.

```bash
D="$(python3 scripts/paths.py --data)"
python3 scripts/render_cv.py "$D/cv-<variant>.md" --letter "$D/cover-letter-<variant>.md" \
    --decisions "$D/cv-decisions.json" \
    --layout sidebar-dark --palette forest --head-font lora --body-font source-sans \
    --role "<the job title>" --employer "<the employer>" --pdf
```

One run writes both PDFs, so the two files cannot end up on different skins by being
printed at different moments. `--decisions` is on it for the same reason it is on every
other render: this run reprints the CV as well as the letter, and without it the CV PDF
reverts to the markdown.

**Where there is no advertisement, the letter is still there to write.** A studio built
without `--letter` shows the letter as a scaffold of prompts: the addressee block, a
`RE:` line, a salutation, four to six body paragraphs and a sign-off, each one a line
that can be clicked, filled in or taken off. Write the letter at the top of the page
takes a whole letter at once, pasted or typed, and the studio hands it back as markdown
under the render command so it prints on the CV's own skin.

**Leave the prompts alone until they ask.** A prompt is a question the page is asking
the person, and filling it in for them is writing a letter nobody asked for. Phase 7
runs when they want a letter. Until then the prompts stay, they never print, and Save
as PDF prints the resume on its own and says why.

Then build the studio once more with `--letter` added, so the letter can be marked up
the same way the CV was. The studio has a Resume and Cover letter chooser under
Document in the Skin tab. Both documents wear the same skin, because they are posted
together, and every line of the letter can be marked up exactly like a line on the CV.

**The rebuild rule holds through this phase as well.** A paragraph of the letter
rewritten, taken off or added brings a fresh studio back in the same reply, on the same
`--role` and `--employer`, exactly as a change to the CV does. See *Rebuild the studio
every time the page changes* in SKILL.md and `references/studio.md`.

**Done when:** it is one page, every claim in it traces to the record, and there is not
one defensive sentence in it.
