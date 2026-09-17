# Assembling, aligning and rendering

## The markdown file is the CV

`cv-<variant>.md` is the master. It is what the person edits, what they read, what
they copy into a portal, and what any renderer renders. It is plain, complete and
readable on its own.

That is only true when the file actually holds everything the person decided, and
`scripts/assemble.py` is what puts it there.

**The ledgers never render.** A renderer that reads the facts ledger will print things
nobody chose. That is not a hypothetical: an earlier version of this workflow rendered
straight from the ledger, and any ledger line not explicitly accounted for printed
verbatim on the finished CV, including the reviewer's own working notes. The
separation is the fix. Ledgers hold what is true. The markdown holds what prints.

## Assembling, with assemble.py

```bash
J="$(python3 scripts/paths.py --job <job id>)"
python3 scripts/assemble.py "$(python3 scripts/paths.py --about)/<their CV>.md" \
    --decisions "$J/cv-decisions.json" \
    --out "$J/cv-<variant>.md"
```

The first argument is the CV the studio was built from, which is the markdown written in
Phase 1 and passed as `--cv` in Phase 3 and Phase 4. Every decision in the file was made
against that document, so assembling from anything else lands the ids on the wrong lines.

| Flag | What it does |
|---|---|
| `--decisions` | the `cv-decisions.json` the studio saved. Required |
| `--out` | the assembled markdown to write, normally `cv-<variant>.md`. Required, and it refuses to write over the source |
| `--archive` | where the record of every removal and every rewrite goes. Defaults to `cv-<variant>-archive.md` beside `--out` |
| `--variant` | the name of this version. Read off the `--out` filename when it is left out |
| `--no-archive` | writes no archive. Only for a run being thrown away, because a removal with no archive is a deletion |

Exit 0 means it wrote the file. Exit 1 means it refused and said the reason. Exit 2 means
the command line was wrong.

### What comes out

**The assembled markdown holds everything.** Every rewrite is in the person's own
wording, every line they took off is gone, every line they added is in the place they
added it, every list is in the order they put it in, and every extra section they ticked
is written in under its own heading, in the case the file uses for its other headings.
The work is done on the raw lines, so everything nobody decided anything about is copied
through byte for byte: the headings, the blank lines, the indentation, the wrapping and
the person's own punctuation. Assembling with an empty decisions file gives back the file
it was handed, byte identical. A file with Windows line endings goes back out with
Windows line endings.

**`cv-<variant>-archive.md` holds what came off.** Every line taken off is in it in full,
with its id, its wording, the reason where the decisions file gives one, and the date.
Every rewrite is in it with the wording before and the wording after. It is appended to
on each pass, it is never rewritten, and it is the durable record: a person who wants a
line back has a file to open and can put it back by hand. The studio's own archive panel
lives in one browser tab and goes when the tab does, so this file is the one to point
anybody at.

**The last line of the assembled markdown is one HTML comment** saying which decisions
are baked in. It never prints, it does not affect the line count, and it is what lets
`render_cv.py` recognise decisions it has already got. Nobody edits it by hand.

**It prints what it did.** Every rewrite, every line taken off with its id and its
wording, every line added, every list reordered and every section written in. That is the
account of what changed and the only place it is given: after the assembly the render has
nothing left to apply, so it reports none of this. It also names anything in the
decisions file that this CV has no line for, on stderr, so an id that matches nothing is
read rather than silently ignored.

**It refuses rather than writing something wrong.** A decisions file that is not valid
JSON or is the wrong shape, an `--out` that is the source file, a source whose line count
does not balance, an order that names a line twice or names one that is not there: each
of those stops the run with the reason said in plain words and nothing written. It also
renders both routes and compares them, so an assembled file that would print anything
other than what the source plus the decisions print is refused as a fault in the script.

### Ids are positional, so close the proposals out first

An id such as `professional-experience/2/b3` names a line by where it sits. After the
assembly those ids name lines of the assembled document, so a proposal, a note or a
hand-to-AI line still carrying a pre-assembly id points at the wrong line, and a
proposal for a line the person took off names nothing at all. Record every decision
against its proposal before assembling. Anything the person wants to change after that
belongs in a new studio built from the assembled CV, where the ids and the page agree.

### Rendering an assembled CV

Rendering `cv-<variant>.md` with no `--decisions` at all now produces the correct
document, because everything is in the markdown. Keep passing `--decisions` anyway.
`render_cv.py` reads the note at the foot, recognises the decisions the file already
holds, applies nothing and says so in one sentence, and a person who makes new decisions
in a studio built from the assembled CV gets those applied normally, because they are
relative to the assembled document.

The hazard that is left is a markdown nobody assembled, and a decisions file changed
after it was baked in. See "Rendering, if the person wants a designed version at all"
below.

### Checking it

`python3 scripts/check.py --job <job id>` reads each `cv-*.md` against the decisions file beside it and
names anything the two disagree about: a line the decisions take off that the markdown
still holds, a line the person added that is missing from it, a rewrite the file has not
taken, a ticked section that is not there. Each fault comes with the `assemble.py`
command that fixes it. The CV as it arrived is never audited this way, because a source
is supposed to still hold every line somebody decided to take off.

## The format

```markdown
# FULL NAME

email | location | linkedin
[eligibility line, if the person decides to carry one]

## PROFILE

Three short paragraphs at most. Third person with no pronouns where the profile is being
written from nothing; the person the CV already uses where it is not.

## KEY SKILLS

**Group name:** item (Level); item (Level); item (Level)

One line per group. Levels in brackets exactly as the person wrote them. Never
more than about nine groups, because this becomes a narrow column in most layouts.

## PROFESSIONAL EXPERIENCE

### Job Title, Employer, Location | 2023 to 2026

One paragraph of scope: what the role was accountable for, at what scale, under what
constraint.

- Bullet, past tense, outcome before activity where an outcome exists
- Bullet

### Job Title, Employer, Location | 2019 to 2022

...

## EDUCATION

**Qualification**, Institution, Location. Status if the qualification was not conferred,
stated plainly and without brackets or apology.

## TRAINING AND CERTIFICATIONS

- Name, Issuer (Year)
```

**The eligibility line is the person's call, and it is put to them as a proposal.**
Citizenship, a right to work, a licence, a clearance. It costs a line a criterion could
have used and most application forms ask for it in a field of their own, so it is often
answered twice. Where the advertisement makes it a condition, having it on the page means
a screener reading only the CV can see it settled. Write the trade into `Why:`, leave
`Decision:` blank, and let them answer. Putting it on unasked and taking it off unasked
are both silent edits to what the employer is told about them. The same holds for
referees. `references/achievements.md` says the same thing from the other end.

Rules that are not optional:

- **No em dashes or en dashes**, including in date ranges. Use "2023 to 2026".
- **Every role with an end date is entirely past tense**, including the scope paragraph.
- **Levels appear in brackets after the item**, because most renderers do not have a
  place to put a separate level field and will silently drop it.
- **A role's bullets are ordered by what this employer weighs**, not chronologically
  within the role. The first bullet gets read; the eighth may not.

## Variants

One facts ledger, several `cv-<variant>.md` files. A variant chooses which facts
print and how they are worded for an audience. A variant never changes what is true.

Name them for the audience they are written for: `cv-<audience>.md`, one file per
audience.

## Aligning variants

Run this whenever a second variant exists, whenever an old one resurfaces, and
whenever a fact is corrected in one of them.

Nominate one variant as current. Then compare every other variant against it and
produce an alignment report in the phase 4 proposal format, split into:

1. **Critical.** A variant claims a role is current when it has ended. A tense left
   behind after a date change. Anything that misstates employment.
2. **The two documents contradict each other.** Same fact, different statement. A
   level, a team size, an education status, the size of a verb. These matter because a
   recruiter may hold both.
3. **Mechanical.** Product names, typos, missing punctuation that breaks a sentence.
4. **Not a contradiction, worth knowing.** Different figures counting different things.
   Say what each covers so the person can answer if asked.

**A correction propagates to every variant. A tailoring choice does not.** A tool that
prints on one variant and is left off another is deliberate. Two different levels for
the same skill is drift.

## Rendering, if the person wants a designed version at all

Rendering is the last step of Phase 6, it is optional, and the markdown is finished
before it starts. Phase 7 is the cover letter, so rendering is not the end of the
work, and a cover letter written afterwards gets rendered on the same skin with
`--letter`.

**Render the assembled file, and keep `--decisions` on the command.** Two things can
still go wrong, and neither is the assembled file itself. A markdown nobody assembled,
one written by hand or the CV as it arrived, carries no note at the foot, so rendering it
without `--decisions` prints the markdown alone: every line they took off comes back,
every line they added is missing, every reorder is undone, any section they ticked is not
there, and the line count still balances because the markdown really does account for all
of its own lines. A decisions file changed after it was baked in no longer matches the
note, because the note records what the file does to the page, so its additions print
twice and its reordered lists shuffle again. `render_cv.py` says that on stderr. The
answer to both is to assemble again from the source.

**The rendering contract:**

- It renders `cv-<variant>.md`. It reads nothing else.
- It adds nothing. No line appears that is not in the markdown.
- It drops nothing. If content does not fit the page count, it **reports what
  overflows and stops.** It never clips, never truncates a column, never silently
  omits a section.
- It preserves every level, every bracket and every figure exactly.
- After rendering, open the result and read all of it before handing it over. Reading
  the source is not the same as seeing the page. Overflow, clipping and dropped
  fields are only visible in the render.

**If a renderer cannot honour that contract, do not use it.** A markdown CV the person
can paste into anything is a better deliverable than a designed one that quietly
disagrees with its own source. Producing a Word or PDF version from the markdown is a
formatting job, and the formatting must not become an editing job.

## Companion documents

A statement of claims, a pitch or a cover letter is assembled the same way: from the
facts ledger, against the asks ledger, in the person's voice, to the word limit the
advertisement sets.

**The advertisement's format instruction always wins over any default in this skill.**
If the pack asks for an 800 word statement, write 800 words. If it asks for no cover
letter, do not produce one unless the person asks. The length a cover letter runs to
when nothing says otherwise is set in `references/cover-letter.md`, which is one page
and four to six paragraphs, and that file is the only place a figure for it belongs.

**A companion document must not restate the CV.** Its job is to say the thing the CV
cannot: that a thing the employer asked for and a thing the person did are the same
work. Before finishing one, list what it covers and check that against the CV and
against any other companion document. Overlap is the most common weakness in these
and it is entirely avoidable.

**Where an advertisement publishes criteria the application must answer, structure
the document around them**, using their headings. Where hiring works that way
this is not a stylistic preference: a criterion the panel cannot see addressed is
generally treated as one that was not met.

**Where the advertisement requires disclosure of AI assistance, tell the person
plainly** and draft the disclosure sentence for them to put in their own words.
