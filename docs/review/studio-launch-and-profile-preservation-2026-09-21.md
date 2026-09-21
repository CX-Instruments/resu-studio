# Studio launch and profile preservation

The reported 0.7.0 run opened many invalid browser tabs and displayed only a middle
paragraph as the original profile. Short mode samples then lost the breadth and
distinctive contribution of the supplied profiles. This investigation concerns the
plugin workflow, not an edit to a real applicant's files.

## Findings

- `build_studio.py` writes HTML but does not launch a browser. The skill delegated
  opening to the agent, suggested a Windows `start` command, and had no attempt limit.
  The supplied screenshot shows addresses such as `builder/4` and `finished/`,
  strongly indicating a path split at spaces into multiple browser arguments. The
  original executed command is unavailable, so its exact construction is unconfirmed.
- The build printed filesystem paths but no ready-to-deliver named HTML links.
- Sample validation accepted any correctly quoted profile paragraph as the entire
  original. The UI could therefore label a middle excerpt as the profile summary.
- Direct mode requested a compact profile; general budget instructions required
  additions to displace content or obtain permission for growth. Those directions
  conflicted with the intended augmentation and preservation of the candidate's case.
- Markdown assembly did not separate additions anchored to a paragraph with blank
  lines, allowing several intended profile paragraphs to merge into one on read-back.

## Corrections

- `open_studio.py` validates a generated HTML target and passes exactly one encoded
  file URL to a browser, without shell interpolation. A persistent, atomically created
  attempt marker prevents repeats, including after a failed launch or a rebuild.
  Explicit user-requested reopening uses `--again`. A dispatched process is not
  treated as proof that the user saw a tab. Cloud sessions deliver files instead.
- The build emits named Resu Studio and Resu Desk Markdown links. Handoff instructions
  require both in the reply and tell the user to refresh after rebuilding.
- Comparisons require every original profile paragraph/bullet in source order and
  preserve paragraph boundaries. Legacy comparison views recover the full original
  from the saved source without altering stored decisions or selected modes.
- Each mode produces a real rewrite in its tone and positioning; that direction carries
  through the selected full rewrite. Original means the faithful source quotation.
  Substance preservation applies to meaning, evidence, pillars and distinctive value,
  not a requirement to retain the source phrasing or sentence order. Condensation and
  page savings are not rewriting goals. Short comparison rewrites are labelled as
  samples, and their length does not set the full rewrite's target.
  Full profile generation requires at least four substantive paragraphs, retaining
  more when needed. Profile changes are checked by assembling their proposed structure
  before publication. Additions preserve actual Markdown paragraph boundaries.
- The instructions require retention of breadth, methods, ownership, technical detail,
  constraints, stakeholders, proof, evidenced pillars and distinctive contribution.
  Existing length is a baseline; only explicit user/application limits require
  tradeoffs. A required preservation review traces source substance into the draft.

## Limits

Paragraph counts, exact-source checks and claim references are mechanically checked.
Whether a paragraph is substantive and preserves the candidate's meaning still needs
an agent to read the full source and proposed text. Four empty or repetitive paragraphs
do not satisfy the writing instructions. Existing source material and the person's
accept/reject/manual decisions are not rewritten by these checks.

These changes are included in 0.7.1. Updating the plugin does not modify an already
generated Studio file; rebuild it to use the updated interface and refresh writing
samples where needed. The 0.7.0 release archive remains unchanged.

## Validation

- All 21 writing tests pass, including real headless browser interaction, complete
  original display, legacy source recovery, no source mutation during previews,
  rejection of a two-paragraph replacement, and four-paragraph assembly/read-back.
- All four launcher tests pass without opening a real desktop browser: one complete
  URL for multiword paths, special-character encoding, repeat suppression, failure
  suppression, explicit reopening, and template/missing-file rejection.
- PDF reading order, jobs, job builds, Desk, data-folder and end-to-end suites pass.
  The documented-command suite passes all 19 checks with Git Bash on PATH.
- The Python-finder test initially failed in the sandbox because its expected
  temporary `config/python.txt` was absent. During 0.7.1 release verification, rerunning
  the unchanged test outside the sandbox with Git Bash on PATH passed all eight checks,
  including both shell and PowerShell discovery. All ten suites have passed across
  these runs.
- The 0.7.1 archive was extracted and all 21 writing/browser tests passed against the
  packaged code without skips. All 106 archive entries match the release source;
  README links resolve, private data directories are excluded, and Python/JavaScript
  syntax checks pass.
- Plugin manifest validation and `git diff --check` pass. The generic skill validator
  rejects the pre-existing `compatibility` frontmatter field; it was retained because
  this work does not change the plugin's host-compatibility metadata.
