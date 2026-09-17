# Multiple job ads and Resu Desk: build plan

Branch: `feature/multi-job-desk`, from `main` at 517b324 (v0.5.0).

## Decisions

1. **A folder per job.** Each advertisement gets its own working folder. Several can be open at once.
2. **Resu Desk is a built HTML file**, made by a script, rebuilt on every change, the same way the Studio is.
3. **Standard tracker stages:** Saved, Scoring, Tailoring, Ready, Applied, Interview, Offer, Rejected, Withdrawn.
4. **`studio.html` is not changed.** Its features and elements stay exactly as they are.

## Why the Studio needs no changes

- `studio_filename()` already puts role and employer in the file name.
- The browser store is already keyed per application (`cvwb:<role-employer>`).
- `documents.protect()` already keeps an earlier Studio instead of writing over it.

What stops multiple jobs today is the working files. `asks.md`, `scorecard.md`, `scorecard-before.md`, `proposals.md`, `achievements.md`, `cv-decisions.json`, `cv-<variant>.md`, its archive and `cover-letter-<variant>.md` all sit loose in the data folder, and Phase 1 replaces them when a new ad arrives.

## Folder layout

```
~/.resu-studio/
  facts.md                 shared, one per person (unchanged)
  answers.md               shared (unchanged)
  cv-source/               shared (unchanged)
  documents.json           shared ledger of every document (unchanged)
  jobs/
    acme-data-analyst-2026-09/
      job.json             id, role, employer, link, closing date, stage, stage history, notes, depth, scores
      ad/                  the ad and job pack, verbatim, with .txt beside each
      asks.md
      scorecard.md
      scorecard-before.md
      proposals.md
      achievements.md
      cv-decisions.json
      cv-<variant>.md
      cv-<variant>-archive.md
      cover-letter-<variant>.md
  _Your Documents Are Here/
    Resu Desk.html
    Acme - Data Analyst/
      Data Analyst - Acme - Studio.html
      <Name> - Data Analyst - Acme - 20260917 - CV.pdf
```

Job id: `<employer>-<role>-<yyyy-mm>`, slugged, with `-2`, `-3` added on a clash.

Depth moves from `answers.md` frontmatter into `job.json`, because it is chosen per ad.

## Script changes

| File | Change |
|---|---|
| `scripts/jobs.py` (new) | `new`, `list`, `show`, `stage <id> <stage>`, `note`, `set`. Owns `job.json` and the stage list. |
| `scripts/paths.py` | `--job <id>` resolves `jobs/<id>/`. `--job-dir`, `--job-documents`. Existing flags unchanged. |
| `scripts/check.py` | Accept a job folder, and find `facts.md` one level up in the data folder. |
| `scripts/build_studio.py` | Default `--out` goes to the job's documents subfolder when `--job` is given. Records the job id in `documents.json`. Rebuilds the Desk after writing. |
| `scripts/render_cv.py` | Same default output rule for PDFs. |
| `scripts/documents.py` | Records carry `job`. `python3 scripts/documents.py` groups by job. |
| `scripts/build_desk.py` (new) | Reads every `job.json` plus `documents.json`, writes `Resu Desk.html`. |
| `assets/desk.html` (new) | Desk template, same design tokens and fonts as the Studio. |
| `templates/job.json` (new) | The shape of a job record. |

## Moving existing data

The first run that sees loose job files in the data folder copies them into `jobs/<id>/`, using the role and employer from `documents.json` or `scorecard.md`. Copy only. Nothing is moved or deleted, nothing already in the job folder is written over, and it says what it did. Same pattern as `paths._bring_forward`.

## Resu Desk

- One row per job: employer, role, stage, closing date, score before and after, last change, links to Studio and PDFs.
- Filter by stage, sort by closing date.
- Stage, closing date and notes can be changed in the page. Saved in the browser under its own key (`resu-desk`), and returned through **hand to AI** or **Save the desk file** (`desk-updates.json`), the same pattern the Studio uses.
- Links are relative, so they work when the Desk is opened from the person's folder. In a cloud chat, the Desk is handed over with a line saying links work from the folder.

## Skill and docs changes

- `SKILL.md` Phase 1: a new ad creates a job with `jobs.py new` instead of replacing the last one. Every command after that passes `--job`.
- A short "Working on more than one job" section: which job is active is named in chat at the start of every phase.
- `references/where-files-go.md`, `references/studio.md`, `README.md`, `CHANGELOG.md` updated.
- Version bump to 0.6.0 through `tools/sync_version.py`.

## Build order

1. `jobs.py`, `templates/job.json`, `paths.py --job`
2. Existing data copy-forward
3. `check.py`, `build_studio.py`, `render_cv.py`, `documents.py` output paths
4. `build_desk.py` and `assets/desk.html`
5. `SKILL.md` and references
6. Test run with a fake person and two fake ads
