# Assembling, aligning and rendering

## The markdown file is the CV

`cv-<variant>.md` is the master. It is what the person edits, what they read, what
they copy into a portal, and what any renderer renders. It is plain, complete and
readable on its own.

**The ledgers never render.** A renderer that reads the facts ledger will print things
nobody chose. That is not a hypothetical: an earlier version of this workflow rendered
straight from the ledger, and any ledger line not explicitly accounted for printed
verbatim on the finished CV, including the reviewer's own working notes. The
separation is the fix. Ledgers hold what is true. The markdown holds what prints.

## The format

```markdown
# ALEX MORGAN TAYLOR

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

Name them for the audience: `cv-data-reporting.md`, `cv-etl-developer.md`.

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

**A correction propagates to every variant. A tailoring choice does not.** Visual
Studio appearing on a developer CV and not a reporting CV is deliberate. Two different
levels for the same skill is drift.

## Rendering, if the person wants a designed version at all

Rendering is the last step of Phase 6, it is optional, and the markdown is finished
before it starts. Phase 7 is the cover letter, so rendering is not the end of the
work, and a cover letter written afterwards gets rendered on the same skin with
`--letter`.

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
