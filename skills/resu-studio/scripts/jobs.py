"""One working folder per job advertisement, and a small record of where each one stands.

A person rarely applies for one job at a time. When every application shared one
folder, the second advertisement replaced the first one's asks ledger, scorecard,
proposals and letter, and the person had to finish one application before starting
another. So each advertisement now gets its own folder under `jobs/`, and a
`job.json` inside it saying what it is and how far it has got:

    jobs/
      acme-data-analyst-2026-09/
        job.json        role, employer, link, closing date, stage, history, scores, notes
        ad/             the advertisement and job pack, verbatim
        asks.md, scorecard.md, proposals.md, achievements.md, cv-decisions.json,
        cv-<variant>.md, cover-letter-<variant>.md

What belongs to the person and not to one application, `facts.md`, `answers.md` and
`cv-source/`, stays in their folder and is read by every job.

Finished documents for a job go in their own folder too, inside
`_Your Documents Are Here/`, named `<Employer> - <Role>`.

    python3 scripts/jobs.py new --role "Data Analyst" --employer "Acme" [--link URL]
                                [--closes 2026-10-01] [--reference R123] [--location Sydney]
    python3 scripts/jobs.py list [--json]
    python3 scripts/jobs.py show <job>
    python3 scripts/jobs.py stage <job> Applied [--on 2026-09-20]
    python3 scripts/jobs.py note <job> "Recruiter called, interview next week"
    python3 scripts/jobs.py set <job> closes 2026-10-01
    python3 scripts/jobs.py score <job> --scorecard <scorecard.md> --as before|after

`<job>` is the id, or the start of exactly one id.

Exit codes: 0 done, 2 wrong command line, 3 no such job, 4 refused (a duplicate, or a
value that is not allowed).
"""

import argparse
import datetime
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import paths  # noqa: E402

SCHEMA = 1

#: Every stage a job can be at, in the order an application usually moves through
#: them. A job can be set to any of them at any time: people withdraw from a job they
#: have not scored yet, and some employers phone before anything was sent.
STAGES = ("Saved", "Scoring", "Tailoring", "Ready", "Applied",
          "Interview", "Offer", "Rejected", "Withdrawn")

#: A job at one of these is finished with. It no longer blocks a new job for the same
#: role at the same employer, and the Desk lists it below the open ones.
CLOSED = ("Rejected", "Withdrawn")

#: The fields `set` may change. `id`, `stage`, `history`, `scores` and `notes` each
#: have a command of their own, and `documents_folder` is fixed when the job is made.
SETTABLE = ("role", "employer", "link", "reference", "location", "closes", "depth")

DEPTHS = ("essentials", "all")

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def today():
    return datetime.date.today().isoformat()


def slug(text):
    """Letters, digits and single hyphens. The same rule `build_studio.slug` uses."""
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", (text or "").lower())).strip("-")


def safe_folder_name(text):
    """A name that is a legal folder name on Windows, a Mac and Linux alike."""
    text = re.sub(r'[\\/:*?"<>|,;]+', " ", text or "")
    return re.sub(r"\s+", " ", text).strip().strip(".")[:70]


def _norm(text):
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def valid_date(text):
    """True for a real calendar date written YYYY-MM-DD. Empty is allowed: it clears."""
    if not text:
        return True
    if not DATE_RE.match(text):
        return False
    try:
        datetime.date.fromisoformat(text)
        return True
    except ValueError:
        return False


def stage_named(given):
    """The stage `given` means, matched without regard to case, or None."""
    for s in STAGES:
        if s.lower() == (given or "").strip().lower():
            return s
    return None


# ------------------------------------------------------------------ the record

def load(job_id):
    """The job's record. Raises paths.NoSuchJob when there is no such job."""
    with io.open(paths.job_file(job_id), encoding="utf-8") as fh:
        return json.load(fh)


def save(rec):
    """Write the record whole, through a temporary file, so a crash cannot leave half."""
    rec["updated"] = today()
    target = os.path.join(paths.jobs_root(), rec["id"], "job.json")
    tmp = target + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(rec, indent=2, ensure_ascii=False) + "\n")
    os.replace(tmp, target)
    return target


def all_jobs():
    """Every job record that can be read, open ones first, then by closing date."""
    out = []
    for jid in paths.known_jobs():
        try:
            out.append(load(jid))
        except (IOError, OSError, ValueError) as e:
            sys.stderr.write("jobs.py: could not read %s/job.json (%s), so it is left "
                             "out.\n" % (jid, e))
    return sorted(out, key=lambda r: (r.get("stage") in CLOSED,
                                      r.get("closes") or "9999-99-99",
                                      r.get("id")))


def open_duplicates(role, employer):
    """Jobs still open for this role at this employer."""
    return [r for r in all_jobs()
            if _norm(r.get("role")) == _norm(role)
            and _norm(r.get("employer")) == _norm(employer)
            and r.get("stage") not in CLOSED]


def new_id(role, employer, on=None):
    """`<employer>-<role>-<yyyy-mm>`, with -2, -3 added until it is free."""
    month = (on or today())[:7]
    base = "-".join(b for b in (slug(employer), slug(role), month) if b)[:80].strip("-")
    base = base or "job-" + month
    taken = set(paths.known_jobs())
    root = paths.jobs_root()
    jid, n = base, 1
    while jid in taken or os.path.exists(os.path.join(root, jid)):
        n += 1
        jid = "%s-%d" % (base, n)
    return jid


def documents_folder_for(role, employer, jid):
    """`<Employer> - <Role>`, or the id when neither gives a usable name.

    Two open jobs can share a role and employer only when `--again` was given, and
    then the folder name carries the id's suffix so their documents stay apart.
    """
    name = " - ".join(b for b in (safe_folder_name(employer), safe_folder_name(role)) if b)
    if not name:
        return jid
    used = set()
    for r in all_jobs():
        used.add((r.get("documents_folder") or "").lower())
    if name.lower() in used:
        m = re.search(r"-(\d+)$", jid)
        name = "%s (%s)" % (name, m.group(1) if m else jid)
    return name


def create(role, employer, link="", reference="", location="", closes="", depth="",
           again=False):
    """Make the folder and its record. Returns the record.

    Raises ValueError, with a sentence fit to show, when refused.
    """
    role, employer = (role or "").strip(), (employer or "").strip()
    if not role:
        raise ValueError("--role is required: it names the job's folder and its documents.")
    if not valid_date(closes):
        raise ValueError("--closes must be a date written YYYY-MM-DD, not %r." % closes)
    if depth and depth not in DEPTHS:
        raise ValueError("--depth is one of %s, not %r." % (", ".join(DEPTHS), depth))
    if not again:
        dups = open_duplicates(role, employer)
        if dups:
            raise ValueError(
                "there is already an open job for %s%s: %s. Work in that one, or pass "
                "--again if this really is a second application for the same job."
                % (role, (" at " + employer) if employer else "",
                   ", ".join(d["id"] for d in dups)))
    jid = new_id(role, employer)
    folder = os.path.join(paths.jobs_root(), jid)
    os.makedirs(os.path.join(folder, "ad"))
    on = today()
    rec = {
        "schema": SCHEMA,
        "id": jid,
        "role": role,
        "employer": employer,
        "documents_folder": documents_folder_for(role, employer, jid),
        "link": (link or "").strip(),
        "reference": (reference or "").strip(),
        "location": (location or "").strip(),
        "closes": closes or "",
        "depth": depth or "",
        "stage": "Saved",
        "history": [{"stage": "Saved", "on": on}],
        "scores": {"before": None, "after": None},
        "notes": [],
        "created": on,
    }
    save(rec)
    return rec


def set_stage(job_id, stage, on=None):
    """Move a job to a stage and add it to the history. Returns the record."""
    name = stage_named(stage)
    if not name:
        raise ValueError("%r is not a stage. The stages are: %s."
                         % (stage, ", ".join(STAGES)))
    on = on or today()
    if not valid_date(on) or not on:
        raise ValueError("--on must be a date written YYYY-MM-DD, not %r." % on)
    rec = load(job_id)
    rec["stage"] = name
    rec.setdefault("history", []).append({"stage": name, "on": on})
    save(rec)
    return rec


def add_note(job_id, text, on=None):
    text = (text or "").strip()
    if not text:
        raise ValueError("a note needs some text.")
    rec = load(job_id)
    rec.setdefault("notes", []).append({"on": on or today(), "text": text})
    save(rec)
    return rec


def set_field(job_id, field, value):
    if field not in SETTABLE:
        raise ValueError("%r cannot be set this way. These can: %s."
                         % (field, ", ".join(SETTABLE)))
    value = (value or "").strip()
    if field == "closes" and not valid_date(value):
        raise ValueError("closes must be a date written YYYY-MM-DD, not %r." % value)
    if field == "depth" and value and value not in DEPTHS:
        raise ValueError("depth is one of %s, not %r." % (", ".join(DEPTHS), value))
    if field == "role" and not value:
        raise ValueError("a job cannot have an empty role.")
    rec = load(job_id)
    rec[field] = value
    save(rec)
    return rec


# ------------------------------------------------------------------ scores

_COUNT_KEYS = ("asks_total", "must", "you_have", "a_reader_would_find", "unscored")


def scorecard_counts(path):
    """The counts from a scorecard's frontmatter, as a dict of ints, or None.

    Only the frontmatter is read. The counts there are what the scorecard says it
    found; tallying the table here as well would be a second opinion that can
    disagree with the first.
    """
    try:
        text = io.open(path, encoding="utf-8").read()
    except (IOError, OSError):
        return None
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
    if not m:
        return None
    out, depth, in_counts = {}, "", False
    for line in m.group(1).splitlines():
        if re.match(r"^depth:\s*", line):
            depth = line.split(":", 1)[1].strip()
        if re.match(r"^counts:\s*$", line):
            in_counts = True
            continue
        if in_counts:
            km = re.match(r"^\s+(\w+):\s*(\d+)\s*$", line)
            if km:
                if km.group(1) in _COUNT_KEYS:
                    out[km.group(1)] = int(km.group(2))
                continue
            if line and not line[0].isspace():
                in_counts = False
    if not out:
        return None
    if depth:
        out["depth"] = depth
    return out


def record_score(job_id, scorecard, which):
    if which not in ("before", "after"):
        raise ValueError("--as is before or after, not %r." % which)
    counts = scorecard_counts(scorecard)
    if not counts:
        raise ValueError("%s has no counts in its frontmatter, so there is no score "
                         "to record. templates/scorecard.md shows the shape." % scorecard)
    counts["on"] = today()
    rec = load(job_id)
    rec.setdefault("scores", {"before": None, "after": None})[which] = counts
    if counts.get("depth") and not rec.get("depth"):
        rec["depth"] = counts["depth"]
    save(rec)
    return rec


# ------------------------------------------------------------------ printing

def _score_text(s):
    if not s:
        return "-"
    total = s.get("asks_total")
    have, find = s.get("you_have"), s.get("a_reader_would_find")
    if total:
        return "%s/%s have, %s/%s found" % (have, total, find, total)
    return "%s have, %s found" % (have, find)


def describe(rec):
    lines = [
        "%s" % rec["id"],
        "  role     : %s" % rec.get("role", ""),
        "  employer : %s" % (rec.get("employer") or "-"),
        "  stage    : %s" % rec.get("stage", ""),
        "  closes   : %s" % (rec.get("closes") or "-"),
        "  link     : %s" % (rec.get("link") or "-"),
        "  depth    : %s" % (rec.get("depth") or "not chosen yet"),
        "  before   : %s" % _score_text((rec.get("scores") or {}).get("before")),
        "  after    : %s" % _score_text((rec.get("scores") or {}).get("after")),
        "  folder   : %s" % os.path.join(paths.jobs_root(), rec["id"]),
        "  documents: %s" % os.path.join(paths.documents_dir(),
                                         rec.get("documents_folder") or rec["id"]),
    ]
    for n in rec.get("notes") or []:
        lines.append("  note %s : %s" % (n.get("on", ""), n.get("text", "")))
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="jobs.py", description="One folder per job advertisement.")
    sub = ap.add_subparsers(dest="cmd")

    p = sub.add_parser("new", help="start a job for a new advertisement")
    p.add_argument("--role", required=True)
    p.add_argument("--employer", default="")
    p.add_argument("--link", default="")
    p.add_argument("--reference", default="")
    p.add_argument("--location", default="")
    p.add_argument("--closes", default="", help="YYYY-MM-DD")
    p.add_argument("--depth", default="", help="essentials or all, once they have said")
    p.add_argument("--again", action="store_true",
                   help="a second open job for the same role at the same employer")

    p = sub.add_parser("list", help="every job, open ones first")
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("show", help="one job")
    p.add_argument("job")
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("stage", help="move a job to a stage")
    p.add_argument("job")
    p.add_argument("stage", help=", ".join(STAGES))
    p.add_argument("--on", default=None, help="YYYY-MM-DD, default today")

    p = sub.add_parser("note", help="add a note to a job")
    p.add_argument("job")
    p.add_argument("text")

    p = sub.add_parser("set", help="change one field: " + ", ".join(SETTABLE))
    p.add_argument("job")
    p.add_argument("field")
    p.add_argument("value", nargs="?", default="")

    p = sub.add_parser("score", help="record a scorecard's counts against the job")
    p.add_argument("job")
    p.add_argument("--scorecard", required=True)
    p.add_argument("--as", dest="which", required=True, choices=("before", "after"))

    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    if not a.cmd:
        ap.print_help()
        return 2

    try:
        if a.cmd == "new":
            rec = create(a.role, a.employer, a.link, a.reference, a.location,
                         a.closes, a.depth, a.again)
            print("started %s" % rec["id"])
            print(describe(rec))
            return 0

        if a.cmd == "list":
            recs = all_jobs()
            if a.json:
                print(json.dumps(recs, indent=2, ensure_ascii=False))
                return 0
            if not recs:
                print("No jobs yet.")
                return 0
            w = max(len(r["id"]) for r in recs)
            for r in recs:
                print("%-*s  %-9s  closes %-10s  %s%s"
                      % (w, r["id"], r.get("stage", ""), r.get("closes") or "-",
                         r.get("role", ""),
                         (" at " + r["employer"]) if r.get("employer") else ""))
            return 0

        if a.cmd == "show":
            rec = load(a.job)
            print(json.dumps(rec, indent=2, ensure_ascii=False) if a.json else describe(rec))
            return 0

        if a.cmd == "stage":
            rec = set_stage(a.job, a.stage, a.on)
            print("%s is now at %s" % (rec["id"], rec["stage"]))
            return 0

        if a.cmd == "note":
            rec = add_note(a.job, a.text)
            print("noted on %s" % rec["id"])
            return 0

        if a.cmd == "set":
            rec = set_field(a.job, a.field, a.value)
            print("%s: %s is now %s" % (rec["id"], a.field, rec[a.field] or "(empty)"))
            return 0

        if a.cmd == "score":
            rec = record_score(a.job, a.scorecard, a.which)
            print("%s: %s score recorded, %s"
                  % (rec["id"], a.which, _score_text(rec["scores"][a.which])))
            return 0

    except paths.NoSuchJob as e:
        sys.stderr.write("jobs.py: %s\n" % e)
        return 3
    except ValueError as e:
        sys.stderr.write("jobs.py: %s\n" % e)
        return 4
    return 2


if __name__ == "__main__":
    sys.exit(main())
