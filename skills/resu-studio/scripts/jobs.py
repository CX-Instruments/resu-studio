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
    python3 scripts/jobs.py adopt [--dry-run] [--role R --employer E | --job <job>]
    python3 scripts/jobs.py apply-desk <desk-updates.json> [--dry-run]

`apply-desk` writes the changes a person made on Resu Desk: a stage, a closing date, a
new note. Each change says what it replaced, and one whose record has moved on since
the Desk was built is refused, by name, rather than written over the newer value.

`adopt` is for somebody who used this before jobs had folders. Their last
application's working files are still loose in their folder; it copies them into a job,
leaves the originals exactly where they were, and remembers it has done so.

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

    When another job already uses the name, a second application for the same job
    after `--again`, or a fresh one after an earlier job was closed, a number is added,
    `(2)`, `(3)`, so their documents stay apart.
    """
    name = " - ".join(b for b in (safe_folder_name(employer), safe_folder_name(role)) if b)
    if not name:
        return jid
    used = set()
    for r in all_jobs():
        used.add((r.get("documents_folder") or "").lower())
    if name.lower() not in used:
        return name
    n = 2
    while ("%s (%d)" % (name, n)).lower() in used:
        n += 1
    return "%s (%d)" % (name, n)


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


# ------------------------------------------------------------------ bringing old work in

#: The working files one application leaves in the person's folder, from before each
#: job had a folder of its own. Named exactly, because a pattern loose enough to
#: catch a file the person put there themselves would copy it into a job it has
#: nothing to do with. `facts.md`, `answers.md`, `documents.json` and `cv-source/`
#: belong to the person, not to a job, and are never matched.
LOOSE_RE = re.compile(
    r"^(asks\.(md|json)"
    r"|scorecard(-before)?\.md"
    r"|proposals\.md"
    r"|achievements\.md"
    r"|cv-[^/\\]+\.(md|json)"
    r"|cover-letter[^/\\]*\.md)$", re.I)

#: Dropped in the person's folder after the loose files have been brought into a job,
#: holding the size and time of each one. The originals are left where they were, so
#: without this every later run would offer to bring them in again.
ADOPTED = ".adopted-into-jobs.json"


def _stamp(path):
    st = os.stat(path)
    return [st.st_size, int(st.st_mtime)]


def _adopted_record():
    try:
        with io.open(os.path.join(paths.data_dir(), ADOPTED), encoding="utf-8") as fh:
            data = json.load(fh)
            return data if isinstance(data, dict) else {}
    except (IOError, OSError, ValueError):
        return {}


def loose_job_files(include_adopted=False):
    """The loose working files in the person's folder, sorted by name.

    A file already brought into a job, and unchanged since, is left out unless
    `include_adopted` is set. One that has changed since is included again, because
    somebody kept working the old way and that work is not in the job yet.
    """
    base = paths.data_dir()
    done = (_adopted_record().get("files") or {}) if not include_adopted else {}
    out = []
    for name in sorted(os.listdir(base)):
        full = os.path.join(base, name)
        if not os.path.isfile(full) or not LOOSE_RE.match(name):
            continue
        if name in done and done[name] == _stamp(full):
            continue
        out.append(name)
    return out


def guess_application():
    """(role, employer, every application the ledger knows) from documents.json.

    The newest document on record is the application the loose files most likely
    belong to, because each new advertisement used to replace them. It is only a
    guess, and it is always shown to the person before anything is copied.
    """
    import documents
    seen = {}
    for rec in documents.load_ledger(paths.documents_ledger()).values():
        role = (rec.get("role") or "").strip()
        if not role:
            continue
        key = (role, (rec.get("employer") or "").strip())
        seen[key] = max(seen.get(key, ""), rec.get("written") or "")
    ranked = sorted(seen.items(), key=lambda kv: kv[1], reverse=True)
    apps = [k for k, _w in ranked]
    if not apps:
        return "", "", []
    return apps[0][0], apps[0][1], apps


def _stage_from(files):
    """How far the old work had got, read from which files exist. Never further."""
    names = set(n.lower() for n in files)
    if any(n.startswith("cover-letter") for n in names):
        return "Ready"
    if any(n.endswith("decisions.json") for n in names) or "proposals.md" in names:
        return "Tailoring"
    if "scorecard.md" in names or "asks.md" in names:
        return "Scoring"
    return "Saved"


def adopt(role="", employer="", job=None, dry_run=False):
    """Copy the loose working files into a job. Returns a report dict.

    Copies only. Nothing in the person's folder is moved, renamed or deleted, and
    nothing already in the job's folder is written over: a file of the same name
    there is the newer one and is kept, and its name is reported.
    """
    import shutil
    import documents
    base = paths.data_dir()
    files = loose_job_files()
    if not files:
        raise ValueError("there are no loose working files in %s to bring into a job."
                         % base)

    guessed = False
    if job:
        rec = load(job)
    else:
        if not role:
            role, g_emp, _apps = guess_application()
            if not role:
                raise ValueError(
                    "found %s, but nothing on record says which job %s for. "
                    "Ask the person, then pass --role and --employer."
                    % (", ".join(files), "it was" if len(files) == 1 else "they were"))
            employer = employer or g_emp
            guessed = True
        dups = open_duplicates(role, employer)
        rec = dups[0] if dups else None

    report = {"files": files, "guessed": guessed, "dry_run": dry_run,
              "role": rec["role"] if rec else role,
              "employer": rec.get("employer", "") if rec else employer,
              "existing_job": bool(rec), "copied": [], "kept": [], "tagged": 0}

    if dry_run:
        report["job"] = rec["id"] if rec else new_id(role, employer) + " (new)"
        report["stage"] = rec["stage"] if rec else _stage_from(files)
        return report

    if rec is None:
        report["new_job"] = True
        rec = create(role, employer)
        rec["stage"] = _stage_from(files)
        if rec["stage"] != "Saved":
            rec["history"].append({"stage": rec["stage"], "on": today()})
        save(rec)
    folder = os.path.join(paths.jobs_root(), rec["id"])

    import filecmp
    for name in files:
        src = os.path.join(base, name)
        target = os.path.join(folder, name)
        if os.path.exists(target):
            if filecmp.cmp(src, target, shallow=False):
                report["kept"].append(name)
                continue
            # Different wording under the same name: somebody kept working in the old
            # place after the job was made. Neither copy is the obvious winner, so
            # both are kept and the second one says where it came from.
            stem, ext = os.path.splitext(name)
            n, target = 1, os.path.join(folder, "%s (brought in %s)%s" % (stem, today(), ext))
            while os.path.exists(target):
                n += 1
                target = os.path.join(folder, "%s (brought in %s, %d)%s"
                                      % (stem, today(), n, ext))
            report.setdefault("beside", []).append(os.path.basename(target))
            shutil.copy2(src, target)
            continue
        shutil.copy2(src, target)
        report["copied"].append(name)

    # The scores, when the scorecards carry them. scorecard-before.md is the first
    # score and scorecard.md the rescore; with no before file, scorecard.md is the first.
    before = os.path.join(folder, "scorecard-before.md")
    now = os.path.join(folder, "scorecard.md")
    scores = rec.setdefault("scores", {"before": None, "after": None})
    first, second = (before, now) if os.path.isfile(before) else (now, None)
    for which, path in (("before", first), ("after", second)):
        if path and os.path.isfile(path) and not scores.get(which):
            counts = scorecard_counts(path)
            if counts:
                counts["on"] = today()
                scores[which] = counts
                if counts.get("depth") and not rec.get("depth"):
                    rec["depth"] = counts["depth"]
    rec.setdefault("notes", []).append({
        "on": today(),
        "text": "Brought in %d file%s from the folder used before each job had its own: %s."
                % (len(report["copied"]) + len(report.get("beside", [])),
                   "" if len(report["copied"]) + len(report.get("beside", [])) == 1 else "s",
                   ", ".join(report["copied"] + report.get("beside", [])) or "none")})
    save(rec)

    # Say in the documents ledger which job each earlier document belongs to. Only a
    # record with this role and employer, and no job already, is touched.
    ledger_path = paths.documents_ledger()
    ledger = documents.load_ledger(ledger_path)
    for r in ledger.values():
        if (not r.get("job") and _norm(r.get("role")) == _norm(rec["role"])
                and _norm(r.get("employer")) == _norm(rec.get("employer"))):
            r["job"] = rec["id"]
            report["tagged"] += 1
    if report["tagged"]:
        documents.save_ledger(ledger, ledger_path)

    done = _adopted_record()
    stamps = done.get("files") or {}
    for name in files:
        stamps[name] = _stamp(os.path.join(base, name))
    done.update({"job": rec["id"], "on": today(), "files": stamps})
    with io.open(os.path.join(base, ADOPTED), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(done, indent=2, ensure_ascii=False) + "\n")

    report["job"] = rec["id"]
    report["stage"] = rec["stage"]
    return report


def loose_notice():
    """One sentence for anybody listing jobs while old loose files are waiting, or ""."""
    try:
        files = loose_job_files()
    except OSError:
        return ""
    if not files:
        return ""
    return ("%d working file%s from before each job had its own folder %s still loose in "
            "the person's folder (%s). %s scripts/jobs.py adopt --dry-run shows which job "
            "they would go into." % (len(files), "" if len(files) == 1 else "s",
                                     "is" if len(files) == 1 else "are",
                                     ", ".join(files), paths.PY))


# ------------------------------------------------------------------ changes from the Desk

def read_desk_updates(path):
    """The changes out of a desk-updates.json, or out of the pasted hand-to-AI text.

    The hand-to-AI block is prose with the JSON in a fenced block at the end, and an
    assistant may save the whole paste rather than just the JSON. Either is accepted.
    """
    with io.open(path, encoding="utf-8") as fh:
        text = fh.read()
    try:
        data = json.loads(text)
    except ValueError:
        m = re.search(r"```json\s*(\{.*\})\s*```", text, re.S)
        if not m:
            raise ValueError("%s is neither desk-updates.json nor a pasted hand-to-AI block "
                             "with a ```json section, so there are no changes to read." % path)
        data = json.loads(m.group(1))
    if not isinstance(data, dict) or not isinstance(data.get("changes"), list):
        raise ValueError("%s has no list of changes in it. It should be the file Resu Desk "
                         "saves, desk-updates.json." % path)
    return data


def apply_desk(path, dry_run=False):
    """Write the Desk's changes into the job records. Returns a report.

    A stage or a closing date is written only when the record still holds the value the
    Desk showed. When it does not, something else changed that job after the Desk was
    built, most often the assistant moving it on in the chat, and writing the Desk's
    older idea over it would lose that. Those are refused, named, and left for the
    person. A note is only ever added, never replaces anything, so it is never refused
    for being stale; the same note already on the job is skipped.
    """
    data = read_desk_updates(path)
    report = {"applied": [], "refused": [], "skipped": [], "dry_run": dry_run}
    for ch in data["changes"]:
        jid = (ch or {}).get("job", "")
        try:
            rec = load(jid)
        except paths.NoSuchJob as e:
            report["refused"].append("%s: %s" % (jid or "(no job named)", e))
            continue
        name = "%s at %s" % (rec.get("role"), rec.get("employer") or "(no employer)")
        touched = False

        st = ch.get("stage")
        if isinstance(st, dict):
            to = stage_named(st.get("to"))
            if not to:
                report["refused"].append("%s: %r is not a stage, so the stage was left at %s."
                                         % (name, st.get("to"), rec.get("stage")))
            elif rec.get("stage") == to:
                report["skipped"].append("%s: already at %s." % (name, to))
            elif rec.get("stage") != st.get("from"):
                report["refused"].append(
                    "%s: the Desk moved it from %s to %s, but it has been at %s since the "
                    "Desk was built. Left at %s. Ask the person whether %s is still right."
                    % (name, st.get("from"), to, rec.get("stage"), rec.get("stage"), to))
            else:
                rec["stage"] = to
                rec.setdefault("history", []).append({"stage": to, "on": today()})
                report["applied"].append("%s: stage %s to %s." % (name, st.get("from"), to))
                touched = True

        cl = ch.get("closes")
        if isinstance(cl, dict):
            to = (cl.get("to") or "").strip()
            was = rec.get("closes") or ""
            if not valid_date(to):
                report["refused"].append("%s: %r is not a date written YYYY-MM-DD, so the "
                                         "closing date was left as it was." % (name, to))
            elif was == to:
                report["skipped"].append("%s: closing date already %s." % (name, to or "empty"))
            elif was != (cl.get("from") or ""):
                report["refused"].append(
                    "%s: the Desk changed the closing date from %s to %s, but it has been %s "
                    "since the Desk was built. Left as %s. Ask the person which is right."
                    % (name, cl.get("from") or "not set", to or "not set", was or "not set",
                       was or "not set"))
            else:
                rec["closes"] = to
                report["applied"].append("%s: closing date %s to %s."
                                         % (name, was or "not set", to or "not set"))
                touched = True

        note = (ch.get("note") or "").strip()
        if note:
            if any(n.get("text") == note for n in rec.get("notes") or []):
                report["skipped"].append("%s: that note is already there." % name)
            else:
                rec.setdefault("notes", []).append({"on": today(), "text": note})
                report["applied"].append("%s: note added." % name)
                touched = True

        if touched and not dry_run:
            save(rec)
    return report


def refresh_desk():
    """Rebuild Resu Desk after a record changed. A Desk problem never fails the command."""
    try:
        import build_desk
    except Exception as e:                                     # noqa: BLE001
        sys.stderr.write("jobs.py: Resu Desk was not updated (%s).\n" % e)
        return
    build_desk.refresh(quiet=True)


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

    p = sub.add_parser("adopt", help="copy loose working files from before jobs into a job")
    p.add_argument("--role", default="")
    p.add_argument("--employer", default="")
    p.add_argument("--job", default=None, help="an existing job to bring them into")
    p.add_argument("--dry-run", action="store_true", help="say what would happen, change nothing")

    p = sub.add_parser("apply-desk", help="write the changes saved from Resu Desk")
    p.add_argument("file", help="desk-updates.json, or the pasted hand-to-AI text")
    p.add_argument("--dry-run", action="store_true", help="say what would happen, change nothing")

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
            refresh_desk()
            print("started %s" % rec["id"])
            print(describe(rec))
            return 0

        if a.cmd == "apply-desk":
            try:
                r = apply_desk(a.file, a.dry_run)
            except (IOError, OSError) as e:
                sys.stderr.write("jobs.py: could not read %s (%s).\n" % (a.file, e))
                return 2
            head = "would write" if r["dry_run"] else "wrote"
            print("%s %d change%s from Resu Desk" % (head, len(r["applied"]),
                                                    "" if len(r["applied"]) == 1 else "s"))
            for line in r["applied"]:
                print("  done     : %s" % line)
            for line in r["skipped"]:
                print("  no change: %s" % line)
            for line in r["refused"]:
                print("  REFUSED  : %s" % line)
            if r["dry_run"]:
                print("  nothing was changed.")
            elif r["applied"]:
                refresh_desk()
            return 4 if r["refused"] else 0

        if a.cmd == "adopt":
            r = adopt(a.role, a.employer, a.job, a.dry_run)
            verb = "would bring" if r["dry_run"] else "brought"
            print("%s %d file%s into %s" % (verb, len(r["files"]),
                                           "" if len(r["files"]) == 1 else "s", r["job"]))
            print("  role     : %s%s" % (r["role"], "   (guessed from the newest document "
                                          "on record, check with the person)"
                                          if r["guessed"] else ""))
            print("  employer : %s" % (r["employer"] or "-"))
            print("  stage    : %s" % r["stage"])
            if r["dry_run"]:
                print("  files    : %s" % ", ".join(r["files"]))
                print("  nothing was changed.")
                return 0
            if r["copied"]:
                print("  copied   : %s" % ", ".join(r["copied"]))
            if r["kept"]:
                print("  kept     : %s   (already in the job and identical)"
                      % ", ".join(r["kept"]))
            if r.get("beside"):
                print("  beside   : %s   (the job already had a different file of that "
                      "name, so both are kept; ask the person which one is current)"
                      % ", ".join(r["beside"]))
            if r["tagged"]:
                print("  documents: %d earlier document%s now say%s which job %s for"
                      % (r["tagged"], "" if r["tagged"] == 1 else "s",
                         "s" if r["tagged"] == 1 else "", "it was" if r["tagged"] == 1
                         else "they were"))
            refresh_desk()
            print("  the originals are still in %s, untouched." % paths.data_dir())
            if r.get("new_job"):
                print("  the advertisement itself stays in cv-source/. Copy it into %s"
                      % os.path.join(paths.jobs_root(), r["job"], "ad"))
                print("  once you know which file it is.")
            return 0

        if a.cmd == "list":
            recs = all_jobs()
            if a.json:
                print(json.dumps(recs, indent=2, ensure_ascii=False))
                return 0
            notice = loose_notice()
            if notice:
                sys.stderr.write("jobs.py: %s\n" % notice)
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
            refresh_desk()
            print("%s is now at %s" % (rec["id"], rec["stage"]))
            return 0

        if a.cmd == "note":
            rec = add_note(a.job, a.text)
            refresh_desk()
            print("noted on %s" % rec["id"])
            return 0

        if a.cmd == "set":
            rec = set_field(a.job, a.field, a.value)
            refresh_desk()
            print("%s: %s is now %s" % (rec["id"], a.field, rec[a.field] or "(empty)"))
            return 0

        if a.cmd == "score":
            rec = record_score(a.job, a.scorecard, a.which)
            refresh_desk()
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
