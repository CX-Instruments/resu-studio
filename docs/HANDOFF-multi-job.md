# Handoff: multiple job ads and Resu Desk

Read this first if you are picking up branch `feature/multi-job-desk`. The full design is in
`docs/multi-job-plan.md`. This file says where the work stands and how to carry on safely.

## The goal

Resu Studio used to handle one job ad at a time. A new ad replaced the last one's working
files. This branch lets a person work on several applications at once, each kept apart, and
adds **Resu Desk**, an HTML page listing every application with its stage and links.

## Decisions already made by the owner (do not reopen)

1. **One folder per job**: `<data>/jobs/<employer>-<role>-<yyyy-mm>/`.
2. **Resu Desk is a built HTML file** (`build_desk.py` + `assets/desk.html`), rebuilt on every
   change, the same way the Studio is. It is not a hosted page and not just a markdown table.
3. **Stages**: Saved, Scoring, Tailoring, Ready, Applied, Interview, Offer, Rejected, Withdrawn.
   Rejected and Withdrawn count as closed.
4. **`assets/studio.html` must not change.** No features, elements or layout changes. It already
   names its file by role and employer and keys its browser storage (`cvwb:<slug>`) the same way,
   so it is already safe for many jobs.

## Status

| Step | What | State |
|---|---|---|
| 1 | `scripts/jobs.py` (new, list, show, stage, note, set, score), `templates/job.json`, `paths.py --job` | Done, committed as `feat(jobs): one folder per job ad, with job.json and paths --job` |
| 2 | `jobs.py adopt`: copy loose single-job files into a job folder | Done, with `tools/test_jobs.py` and these notes |
| 3 | `build_studio.py`, `render_cv.py`, `check.py`, `documents.py` take `--job` | Done, tested by `tools/test_jobs_build.py` |
| 4 | `build_desk.py`, `assets/desk.html`, `jobs.py apply-desk` | Done, tested by `tools/test_desk.py` |
| 5 | `SKILL.md`, `references/where-files-go.md`, `references/studio.md`, `README.md`, `CHANGELOG.md` | **Next** |
| 6 | Full test run with a fake person and two fake ads, version bump to 0.6.0 via `tools/sync_version.py` | Not started |

Check `git log --oneline` to confirm what has landed.

## What exists now

**`scripts/paths.py`** (additions only, nothing old changed)
- `jobs_root()`, `known_jobs()`, `find_job(given)`, `job_dir(id)`, `job_file(id)`,
  `job_ad_dir(id)`, `job_documents_dir(id)`, exception `NoSuchJob`.
- `find_job` accepts an exact id or a prefix that matches exactly one job. Two matches is refused.
- CLI: `paths.py --jobs`, `paths.py --job <id> [--job-dir|--job-ad|--job-documents|--job-file]`.
  Exit 3 for an unknown job.
- `paths.py` does **not** import `jobs.py` (a circular import there re-runs `resolve()`; see the
  `_BUSY` comment in paths.py).

**`scripts/jobs.py`**
- Owns `job.json`. Writes are atomic (temp file then `os.replace`).
- `new` refuses a second open job for the same role and employer unless `--again`.
- `documents_folder` is fixed at creation (`Employer - Role`, then `(2)`, `(3)` on a clash) so
  renaming a role later does not split documents.
- `adopt` copies files matching `LOOSE_RE` from the data folder root into a job. It never moves,
  deletes or overwrites. A same-name file with different content is kept beside as
  `<name> (brought in <date>).md`. It tags matching `documents.json` records with `"job": <id>`
  and writes `.adopted-into-jobs.json` (name to size and mtime) so it does not repeat.
- `adopt` runs only when asked. `jobs.py list` prints a notice to stderr when loose files wait.
- The ad stays in `cv-source/` after adopt, because the CV and ad were stored together there.
- Exit codes: 0 done, 2 bad command line, 3 no such job, 4 refused.

**`tools/test_jobs.py`**: 13 scenarios, 34 checks, runs in a temp folder with
`CLAUDE_PLUGIN_DATA` pointed at it. Run `python3 tools/test_jobs.py` after any change to
`jobs.py` or `paths.py`. It must print `34 of 34 checks passed` (more once you add checks).

## What step 3 changed

- `build_studio.py --job <id>`: role and employer are read from `job.json` when not passed (passed
  values still win). The studio is written to `paths.job_documents_dir(id)` unless `--out` is given.
  `--role` stays required when there is no `--job`, so every existing command still works. The
  browser store key rule is unchanged (`cvwb:` + slug of role and employer), proven by a test that
  builds the same application both ways and compares the keys.
- `render_cv.py --job <id>`: same role and employer rule. PDFs and the HTML preview go to the job's
  documents folder unless `--pdf-dir`, `--outdir` or `--out` names another. Module global `JOB_ID`
  carries the id into `_record()`.
- `documents.py`: `record()` and `note()` take `job=""` and store it on the record. The listing
  shows `[job <id>]` beside each application that has one.
- `check.py --job <id> [variant]`: checks that job's folder. `facts.md` is looked for in the folder
  first, then two levels up when the folder sits in `jobs/`. Run with no job on a person's folder
  that has `jobs/`, it says to use `--job`.
- Tests: `tools/test_jobs_build.py`, 10 scenarios, 23 checks, uses the fictional CV in
  `docs/review/sample-cv.md`. It prints a PDF, so it needs Chromium, Chrome or Edge (`CV_BROWSER`).

## What step 4 changed

Defaults the owner accepted: a table (not stage columns), new jobs start in chat (not on the
Desk), no extra fields beyond what `job.json` already holds.

- `assets/desk.html` (new): full HTML document, Studio's `:root` colour tokens (light and dark),
  Archivo Narrow embedded by the build, no network. Stage count strip (click to filter), sort by
  closing date, last change or employer, one row per job, closed jobs folded under
  "Closed (n)", a "Next:" hint per stage, closing flags ("closes in 3 days", "closed 1 day ago")
  only for Saved to Ready. Works at 390px wide.
- Editing on the page: stage, closing date, new note. Kept in localStorage under
  `resu-desk:<sha1 of data folder>[:10]` (every call in try/catch). A bottom tray offers
  **hand to AI** (plain summary plus a ```json block), **Save the desk file**
  (`desk-updates.json`, via `claude.use("downloads")` when present, else a Blob download, else
  clipboard) and **Undo all**. On load, `settle()` drops changes the records already hold, so a
  rebuilt Desk opens clean. A row whose record moved on since the change says so on the row.
- `scripts/build_desk.py` (new): `build(out)`, `refresh(quiet)` (never raises, prints one line on
  failure), `desk_data()`. Documents for a job: ledger records with that `job` id, plus older
  records with no job whose role and employer match. Links are relative and URL-quoted; each also
  carries a plain `where` path. Data is embedded with `</` escaped. Atomic write, temp file removed
  on failure. Exit 5 when it cannot write.
- `scripts/jobs.py apply-desk <file> [--dry-run]`: accepts the JSON file or the whole pasted
  hand-to-AI text. Each stage or closing date change carries `from`; if the record no longer
  holds `from`, that change is REFUSED with a sentence naming both values, and the rest still
  apply. Notes are only added, duplicates skipped. Exit 4 when anything was refused. This
  per-field check replaced the plan's "compare the updated date", because `updated` is only a
  date and would refuse unrelated same-day changes.
- Desk rebuild hooks: `jobs.py` after new, stage, note, set, score, adopt and apply-desk (silent);
  `build_studio.py` after writing (prints `desk   : <path>`); `render_cv.py` after `--pdf`.
- Tests: `tools/test_desk.py`, 13 scenarios, 48 checks. Needs Playwright for Python and Chromium.
  Screenshots land in `<temp>/resu-test-desk/shots`.

## Step 5 in detail (next)

Teach the skill to use all of this. Read `SKILL.md` and each reference in full first.

- `SKILL.md` Phase 1: before copying a new ad, run `jobs.py list`. If loose files are reported,
  offer `jobs.py adopt --dry-run`, confirm the job with the person, then `adopt`. For a new ad,
  `jobs.py new --role --employer [--link --closes]` and copy the ad into
  `paths.py --job <id> --job-ad`. Replace the "a new advertisement replaces the last one"
  warning: nothing is replaced now.
- Every later command in SKILL.md passes `--job <id>` and names job files through
  `paths.py --job <id>` (asks.md, scorecard.md, proposals.md, achievements.md,
  cv-decisions.json, cv-<variant>.md, cover-letter-<variant>.md). `facts.md`, `answers.md`,
  `cv-source/` stay where they are. Depth goes into `job.json` with `jobs.py set <id> depth`.
- Stage moves: Phase 3 start `Scoring`, Phase 4 `Tailoring`, after the final PDF `Ready`. Record
  scores with `jobs.py score --as before` after Phase 3 and `--as after` after Phase 6.
- A short "Working on more than one job" section: name the job in chat at the start of every
  phase; never mix two jobs' files; hand over Resu Desk after it changes; when the person pastes a
  Desk block, save it and run `apply-desk`, and read every REFUSED line back to them in plain words.
- `references/where-files-go.md`: the new layout tree, `--job` paths, where the Desk lives.
- `references/studio.md`: `--job` on every build command. The store key rule did not change.
- `README.md`: a short Resu Desk section with a screenshot made from fictional data, and the
  folder layout. `CHANGELOG.md`: an Unreleased section listing steps 1 to 5.
- Check every edited doc for em dashes and en dashes (`check.py` already refuses them in CVs).

## Rules for working in this repo

- **Keep each file's existing line endings.** Most files are CRLF on the owner's Windows machine,
  but `check.py` and `documents.py` are LF. New files are CRLF. Check with `file` first.
- **Python standard library only.** Python 3, runs on Windows, Mac and Linux.
- **Code comments and docstrings** follow the house style: plain prose that explains why,
  written for a careful reader. Read a few functions in `paths.py` before writing new ones.
- **Every refusal is a full sentence** saying what was wrong and what to do instead.
- **Never delete or overwrite a person's file.** Copy, keep beside, or refuse.
- **Test data is always fictional.** Never use the owner's real name, email, phone or LinkedIn in
  fixtures, samples or screenshots. Use an invented person (the tests use Sam Rivera).
- **Writing for the owner**: no em dashes or en dashes, plain language, beginner-friendly
  explanations of tooling. Show evidence of testing, screenshots preferred.
- **Do not bump the version** until step 6.

## Environment notes from the last session

- The session could not run a shell on the owner's Windows machine (a Windows update issue),
  so work was done in a cloud copy and files were written back. Git commands were run by the
  owner. If you can run git locally, confirm `git status` is clean before starting.
- Screenshots were made by rendering the test output to HTML and capturing it with Playwright.
