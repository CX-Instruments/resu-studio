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
| 4 | `build_desk.py` and `assets/desk.html` | **Next** |
| 5 | `SKILL.md`, `references/where-files-go.md`, `references/studio.md`, `README.md`, `CHANGELOG.md` | Not started |
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

## Step 4 in detail (next)

- `scripts/build_desk.py`: read `jobs.all_jobs()` and `documents.load_ledger(paths.documents_ledger())`.
  Group documents by their `job` field. Write `_Your Documents Are Here/Resu Desk.html` from
  `assets/desk.html`, swapping `const` blocks the way `build_studio.swap_const` does.
- One row per job: employer, role, stage, closing date (flag ones closing within 7 days), before
  and after score (`a_reader_would_find` of `asks_total`), last updated, relative links to its
  Studio and PDFs. Open jobs first, closed below.
- Filter by stage, sort by closing date. Stage, closing date and notes editable in the page,
  saved in localStorage under `resu-desk` (wrapped in try/catch), returned through a
  **hand to AI** block and a **Save the desk file** button (`desk-updates.json`), matching the
  Studio's pattern. Then add `jobs.py apply-desk <desk-updates.json>` to write those changes.
- Match the Studio's look: read the `:root` tokens and fonts in `assets/studio.html`. Do not edit it.
- Call `build_desk.py` at the end of `build_studio.py`, `render_cv.py --pdf` and every `jobs.py`
  command that changes a record, so the Desk is never stale. Never let a Desk failure fail those.

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
