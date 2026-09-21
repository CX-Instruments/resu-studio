"""Private application data belongs to the current task workspace.

Default: <workspace>/Resu - CV Builder. The workspace is RESU_WORKSPACE when
explicitly carried from the task's starting directory, otherwise the process cwd.
Plugin installation paths, global location records and host data variables never
select application data. Status does not search for or import older work.

An explicitly requested alternative is recorded only in this workspace's private
.resu/location.json, with the user's instruction. Importing any older folder also
requires that instruction. No operation here deletes or moves existing work.
"""

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)

#: True when Python itself is running on Windows. Then `D:\\CVs` is a real folder
#: this process can open.
ON_WINDOWS = os.name == "nt"

#: How to name Python in a message a person or an agent will copy. Windows installs
#: it as `python` or `py`; `python3` is usually missing there.
PY = "python" if ON_WINDOWS else "python3"

NOT_CHOSEN = 6

# ------------------------------------------------------------------ the names

#: The folder a person is offered, inside their project or their home folder.
TOP = "Resu - CV Builder"

#: Numbered, so they sort in the order a person meets them, and named in plain words,
#: because the person opening this folder may never have opened a terminal.
ABOUT = "1 About me"
RECORD = "2 My record"
JOBS = "3 Jobs"
DOCUMENTS = "4 Finished documents"

#: What the scripts keep for themselves, out of the way.
SYSTEM = ".resu"

#: Where loose working files from before jobs had folders are put by --bring, and
#: where `jobs.py adopt` looks for them.
FROM_BEFORE_JOBS = "from-before-jobs"

#: The names the same things had before, read by --bring.
OLD_SOURCE = "cv-source"
OLD_JOBS = "jobs"
OLD_DOCUMENTS = "_Your Documents Are Here"

# Legacy pointer name retained for compatibility tests; never consulted.
_POINTER = os.path.join(SKILL, "data-location.txt")

README_TEXT = u"""Resu - CV Builder
=================

This folder holds your CV, your working history, the job ads you applied for and the
documents Resu Studio made for you. It is private and belongs to you.

  1 About me             your CV as you gave it, and any links you shared
  2 My record            optional saved history; reused only when you ask
  3 Jobs                 one folder for each job ad
  4 Finished documents   Resu Desk and your finished CVs, letters and Studios

Nothing in here is sent anywhere. The .gitignore file in this folder tells git to ignore
all of it, so it cannot be committed to a repository by accident. Do not share this
folder, and do not remove that .gitignore if this folder sits inside a project.
"""


def utf8_output():
    """Make printing a name like Zoë safe on Windows. Harmless everywhere else."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass


if ON_WINDOWS:
    utf8_output()


def check_pointer_text(raw, where="", require_parent=True):
    """(path, complaint). Exactly one of the two is set.

    Everything refused here is refused because accepting it would look like it
    worked. A drive letter becomes a folder called `D:\\CVs` in whatever directory
    the script was run from; a relative name means a different place depending on
    where somebody ran it; a path whose parent does not exist is almost always a
    typo, and creating it makes the typo permanent.
    """
    import re
    raw = (raw or "").strip().strip('"').strip("'")
    label = (" in %s" % where) if where else ""
    if not raw:
        return None, "the pointer%s is empty." % label

    if not ON_WINDOWS and (re.match(r"^[A-Za-z]:[\\/]", raw) or "\\" in raw):
        msg = ("the pointer%s names %s, which is a Windows path. This session "
               "cannot see drive letters or backslashes, and using it as written "
               "would make one folder whose name contains the backslashes and put "
               "every document in it. Write the path as this session sees it: it "
               "starts with a / and has no backslashes, usually something like "
               "/home/<you>/mnt/<folder>." % (label, raw))
        return None, msg

    path = os.path.expanduser(raw)
    if not os.path.isabs(path):
        return None, ("the pointer%s names %s, which is a relative path. It would "
                      "mean a different folder for every directory a script is run "
                      "from, so it is refused. Write the whole path, %s."
                      % (label, raw, "starting with the drive letter, like D:\\CVs"
                         if ON_WINDOWS else "starting at /"))

    path = os.path.normpath(path)
    parent = os.path.dirname(path)
    if require_parent and not os.path.isdir(path) and not os.path.isdir(parent):
        return None, ("the pointer%s names %s, but %s does not exist. The folder "
                      "itself is created for you; the folder it sits in has to be "
                      "there already, because a path that is a typo would otherwise "
                      "be created as a real folder and everything would go into it."
                      % (label, raw, parent))
    return path, None


def _some(names, limit=6):
    """A few names, said plainly, with a count for the rest."""
    names = list(names)
    shown = ", ".join(sorted(names)[:limit])
    if len(names) > limit:
        shown += " and %d more" % (len(names) - limit)
    return shown


# ------------------------------------------------------------------ which install is this

def _same(a, b):
    return os.path.normcase(os.path.realpath(a)) == os.path.normcase(os.path.realpath(b))


def _within(path, parent):
    try:
        return os.path.commonpath([os.path.realpath(path), os.path.realpath(parent)]) == os.path.realpath(parent)
    except ValueError:
        return False


def workspace_dir():
    """The task workspace, never inferred from the plugin installation location."""
    raw = os.environ.get("RESU_WORKSPACE") or os.getcwd()
    if not os.path.isabs(raw) or not os.path.isdir(raw):
        raise ValueError("Run from the existing task workspace, or set RESU_WORKSPACE to its absolute path.")
    root = os.path.realpath(raw)
    if _within(root, SKILL):
        raise ValueError("The plugin directory is not the task workspace. Run from the user's current folder or carry its path in RESU_WORKSPACE before changing directory.")
    return root


def install():
    """Compatibility tuple: choices now belong to the task workspace."""
    root = workspace_dir()
    return os.path.normcase(root), "project", root


def suggested_folder(where):
    if where == "project":
        return os.path.join(workspace_dir(), TOP)
    if where == "home":
        return os.path.join(os.path.expanduser("~"), TOP)
    return None


def config_dir():
    """Workspace-local metadata; do not read the former global registry."""
    return os.path.join(suggested_folder("project"), SYSTEM)


def locations_file():
    return os.path.join(config_dir(), "location.json")


def recorded_choice():
    """Only an explicit, workspace-scoped instruction can redirect the default."""
    default = suggested_folder("project")
    if not _within(default, workspace_dir()) or not _within(config_dir(), default):
        raise ValueError("The default data folder resolves outside this workspace. Do not follow it or invent another folder; the user must explicitly choose the destination.")
    try:
        with io.open(locations_file(), encoding="utf-8") as fh:
            entry = json.load(fh)
    except FileNotFoundError:
        return None
    except (OSError, ValueError) as exc:
        raise ValueError("The workspace location record cannot be read; no alternative folder was used: %s" % exc)
    if (not isinstance(entry, dict) or entry.get("schema") != 1
            or not all(isinstance(entry.get(k), str) and entry[k].strip()
                       for k in ("workspace", "folder", "user_instruction"))
            or not _same(entry["workspace"], workspace_dir())):
        raise ValueError("The workspace location record lacks an explicit user instruction for this workspace. Do not use it or silently fall back.")
    return entry.get("folder")


def resolve(force=False):
    """Resolve on every call so one process cannot retain another workspace's folder."""
    try:
        chosen = recorded_choice()
        if chosen:
            path, complaint = check_pointer_text(chosen, locations_file(), require_parent=False)
            if complaint:
                raise ValueError(complaint)
            return path, "explicit user choice for this workspace", "chosen"
        return suggested_folder("project"), "current workspace default", "workspace"
    except ValueError as exc:
        sys.stderr.write("resu-studio: %s\n" % exc)
        return None, str(exc), "none"


def not_chosen_message():
    return ("resu-studio: the task workspace or its explicit location record could not be resolved. "
            "Run from the user's current folder or set RESU_WORKSPACE to that same folder. "
            "Do not search elsewhere, invent a folder name, or use older work.")


_PRIVATE_DONE = set()


def ensure_private(path):
    """The README and the `*` .gitignore, written once if missing. Never overwritten."""
    if path in _PRIVATE_DONE:
        return
    _PRIVATE_DONE.add(path)
    for name, text in ((".gitignore", u"# Resu Studio: everything in this folder is private.\n*\n"),
                       ("README.txt", README_TEXT)):
        target = os.path.join(path, name)
        if os.path.exists(target):
            continue
        try:
            with io.open(target, "w", encoding="utf-8", newline="") as fh:
                fh.write(text)
        except (IOError, OSError) as e:
            sys.stderr.write("resu-studio: could not write %s (%s).\n" % (target, e))


def data_dir():
    """The person's own folder. Stops the script, exit 6, when none has been chosen."""
    path, _src, _how = resolve()
    if path is None:
        sys.stderr.write(not_chosen_message() + "\n")
        raise SystemExit(NOT_CHOSEN)
    try:
        ensure_layout(path)
    except ValueError as exc:
        sys.stderr.write("resu-studio: %s\n" % exc)
        raise SystemExit(NOT_CHOSEN)
    return path


def sub(*parts):
    """A named folder inside the person's own folder, created."""
    path = os.path.join(data_dir(), *parts)
    os.makedirs(path, exist_ok=True)
    return path


def system_dir():
    return sub(SYSTEM)


def documents_dir():
    """Where finished CVs, letters, Studios and Resu Desk land."""
    return sub(DOCUMENTS)


def record_dir():
    return sub(RECORD)


def facts_file(job=None):
    """Application evidence; the shared record is never an automatic input."""
    return os.path.join(job_dir(job) if job else record_dir(), "facts.md")


def answers_file(job=None):
    """Answers within the authorised application scope."""
    return os.path.join(job_dir(job) if job else record_dir(), "answers.md")


def documents_ledger():
    """The small record saying which advertisement each document was for."""
    return os.path.join(system_dir(), "documents.json")


def cv_source_dir():
    """The CV as it arrived, and anything else about the person they shared."""
    return sub(ABOUT)


about_dir = cv_source_dir


# ------------------------------------------------------------------ what already exists

def work_in(folder):
    """What Resu Studio work a folder holds, or None when it holds none.

    Reads either layout. Counts only, so `--status` can say what is there without
    anybody's CV being read out into a chat.
    """
    if not folder or not os.path.isdir(folder):
        return None
    j = lambda *p: os.path.join(folder, *p)                   # noqa: E731
    new = any(os.path.isdir(j(n)) for n in (ABOUT, RECORD, JOBS, DOCUMENTS))
    jobs_at = j(JOBS) if new else j(OLD_JOBS)
    docs_at = j(DOCUMENTS) if new else j(OLD_DOCUMENTS)
    about_at = j(ABOUT) if new else j(OLD_SOURCE)
    facts = os.path.isfile(j(RECORD, "facts.md")) or os.path.isfile(j("facts.md"))

    def files(d, exts):
        n = 0
        for here, _dirs, names in os.walk(d) if os.path.isdir(d) else ():
            n += sum(1 for x in names if x.lower().endswith(exts))
        return n

    try:
        jobs = sum(1 for n in os.listdir(jobs_at)
                   if os.path.isfile(os.path.join(jobs_at, n, "job.json")))
    except OSError:
        jobs = 0
    loose = 0
    try:
        import re
        pat = re.compile(r"^(asks\.md|scorecard(-before)?\.md|proposals\.md|cv-.+\.(md|json)|"
                         r"cover-letter.*\.md)$", re.I)
        loose = sum(1 for n in os.listdir(folder) if pat.match(n) and os.path.isfile(j(n)))
    except OSError:
        pass
    summary = {"folder": folder, "layout": "new" if new else "old", "facts": facts,
               "jobs": jobs, "loose_job_files": loose,
               "documents": files(docs_at, (".pdf", ".html")),
               "about_files": files(about_at, ("",))}
    if not (facts or jobs or loose or summary["documents"] or summary["about_files"]):
        return None
    return summary


def existing_work(exclude=None):
    """Automatic discovery is disabled. Only --bring reads a user-named source."""
    return []


# ------------------------------------------------------------------ choosing

def ensure_layout(path):
    for name in (ABOUT, RECORD, JOBS, DOCUMENTS, SYSTEM, "README.txt", ".gitignore"):
        if not _within(os.path.join(path, name), path):
            raise ValueError("The data folder contains a path outside its root: %s. Do not follow it or invent another destination." % name)
    for name in (ABOUT, RECORD, JOBS, DOCUMENTS, SYSTEM):
        os.makedirs(os.path.join(path, name), exist_ok=True)
    _PRIVATE_DONE.discard(path)
    ensure_private(path)


def choose(target, bring_from=None, user_instruction=None):
    """Record an explicit workspace choice, initialise it, and import only if asked.

    Returns a report dict. Raises ValueError with a sentence fit to show.
    """
    key, kind, root = install()
    instruction = (user_instruction or "").strip()
    if (target != "project" or bring_from) and not instruction:
        raise ValueError("An alternative folder or import requires --user-instruction quoting the user's explicit request. Otherwise use the current workspace default.")
    if target == "project":
        folder = suggested_folder("project")
    elif target == "home":
        folder = suggested_folder("home")
    else:
        folder, complaint = check_pointer_text(target, "--choose", require_parent=True)
        if complaint:
            raise ValueError(complaint)
    if bring_from:
        src, complaint = check_pointer_text(bring_from, "--bring", require_parent=True)
        if complaint:
            raise ValueError(complaint)
        if not os.path.isdir(src):
            raise ValueError("--bring names %s, which is not a folder." % bring_from)
        if _same(src, folder):
            raise ValueError("--bring names the same folder that was chosen, so there is "
                             "nothing to copy.")
        bring_from = src

    if not _within(suggested_folder("project"), root):
        raise ValueError("The default folder points outside the workspace; resolve that path with the user before writing.")
    was = recorded_choice() if target != "project" else None
    try:
        os.makedirs(folder, exist_ok=True)
        ensure_layout(folder)
    except OSError as e:
        raise ValueError("%s could not be created (%s)." % (folder, e))

    # Keep redirection metadata inside the canonical workspace folder even when the
    # explicitly chosen data destination is elsewhere. Never touch global settings.
    try:
        if target == "project":
            if os.path.isfile(locations_file()):
                os.remove(locations_file())
        else:
            ensure_layout(suggested_folder("project"))
            entry = {"schema": 1, "workspace": root, "folder": folder,
                     "user_instruction": instruction}
            tmp = locations_file() + ".tmp"
            with io.open(tmp, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(json.dumps(entry, indent=2, ensure_ascii=False) + "\n")
            os.replace(tmp, locations_file())
    except OSError as exc:
        raise ValueError("The explicit choice could not be recorded in this workspace (%s)." % exc)

    report = {"folder": folder, "key": key, "kind": kind, "was": was, "brought": None}
    if bring_from:
        report["brought"] = bring(bring_from, folder)
    return report


# ------------------------------------------------------------------ bringing work in

def _copy_file(src, dst, report):
    import shutil
    if os.path.exists(dst):
        report["kept"].append(os.path.relpath(dst, report["_dest"]))
        return False
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    try:
        shutil.copy2(src, dst)
        report["copied"] += 1
        return True
    except (IOError, OSError):
        report["failed"].append(os.path.relpath(src, report["_src"]))
        return False


def _copy_into(src_dir, dst_dir, report):
    for here, _dirs, names in os.walk(src_dir):
        rel = os.path.relpath(here, src_dir)
        for n in names:
            _copy_file(os.path.join(here, n),
                       os.path.join(dst_dir, n) if rel == os.curdir
                       else os.path.join(dst_dir, rel, n), report)


def bring(src, dest):
    """Copy a folder of Resu Studio work, old layout or new, into `dest`. Returns a report.

    Copies only: `src` is left exactly as it was, and nothing already in `dest` is
    written over. The documents list is merged, and every record in it is pointed at
    the copy of its document, so Resu Desk links to files that are really there.
    """
    import re
    report = {"from": src, "to": dest, "copied": 0, "kept": [], "failed": [],
              "left": [], "records": 0, "_src": src, "_dest": dest}
    ensure_layout(dest)
    new = any(os.path.isdir(os.path.join(src, n)) for n in (ABOUT, RECORD, JOBS, DOCUMENTS))
    if new:
        mapping = [(n, n) for n in (ABOUT, RECORD, JOBS, DOCUMENTS)]
        ledger_src = os.path.join(src, SYSTEM, "documents.json")
    else:
        mapping = [(OLD_SOURCE, ABOUT), (OLD_JOBS, JOBS), (OLD_DOCUMENTS, DOCUMENTS)]
        ledger_src = os.path.join(src, "documents.json")
    for old, now in mapping:
        if os.path.isdir(os.path.join(src, old)):
            _copy_into(os.path.join(src, old), os.path.join(dest, now), report)

    loose = re.compile(r"^(asks\.(md|json)|scorecard(-before)?\.md|proposals\.md|achievements\.md|"
                       r"cv-[^/\\]+\.(md|json)|cover-letter[^/\\]*\.md)$", re.I)
    # locations.json and location are the old shared folder's own settings, not work.
    handled = set(o for o, _n in mapping) | {SYSTEM, ".gitignore", "README.txt", "documents.json",
                                             "locations.json", "location", ".migrated-from-plugin"}
    for n in sorted(os.listdir(src)):
        full = os.path.join(src, n)
        if n in handled:
            continue
        if os.path.isdir(full):
            report["left"].append(n + "/")
        elif n in ("facts.md", "answers.md"):
            _copy_file(full, os.path.join(dest, RECORD, n), report)
        elif loose.match(n):
            _copy_file(full, os.path.join(dest, SYSTEM, FROM_BEFORE_JOBS, n), report)
        elif n == ".adopted-into-jobs.json":
            _copy_file(full, os.path.join(dest, SYSTEM, n), report)
        else:
            report["left"].append(n)
    if new and os.path.isdir(os.path.join(src, SYSTEM)):
        for n in os.listdir(os.path.join(src, SYSTEM)):
            full = os.path.join(src, SYSTEM, n)
            if n == "documents.json":
                continue
            if os.path.isdir(full):
                _copy_into(full, os.path.join(dest, SYSTEM, n), report)
            else:
                _copy_file(full, os.path.join(dest, SYSTEM, n), report)

    # The documents list: every record re-keyed and re-pointed at its copy.
    if os.path.isfile(ledger_src):
        try:
            with io.open(ledger_src, encoding="utf-8") as fh:
                was = json.load(fh)
        except (IOError, OSError, ValueError):
            was = {}
            report["failed"].append("documents.json (not readable)")
        ledger_dest = os.path.join(dest, SYSTEM, "documents.json")
        try:
            with io.open(ledger_dest, encoding="utf-8") as fh:
                here = json.load(fh)
        except (IOError, OSError, ValueError):
            here = {}
        dir_map = [(os.path.join(src, o), os.path.join(dest, n)) for o, n in mapping]
        for k, rec in (was or {}).items():
            if not isinstance(rec, dict):
                continue
            rec = dict(rec)
            p = rec.get("path") or os.path.join(src, k)
            for o, n in dir_map:
                if _same(p, o) or os.path.normcase(os.path.abspath(p)).startswith(
                        os.path.normcase(os.path.abspath(o)) + os.sep):
                    p = os.path.join(n, os.path.relpath(p, o))
                    break
            rec["path"] = os.path.abspath(p)
            try:
                rel = os.path.relpath(rec["path"], dest)
                nk = rel.replace(os.sep, "/") if not rel.startswith(os.pardir) else rec["path"].replace(os.sep, "/")
            except ValueError:
                nk = rec["path"].replace(os.sep, "/")
            if nk not in here:
                here[nk] = rec
                report["records"] += 1
        os.makedirs(os.path.dirname(ledger_dest), exist_ok=True)
        with io.open(ledger_dest, "w", encoding="utf-8", newline="") as fh:
            fh.write(json.dumps(here, indent=2, ensure_ascii=False))

    import time
    try:
        with io.open(os.path.join(dest, SYSTEM, "brought-in.txt"), "a", encoding="utf-8", newline="") as fh:
            fh.write(u"%s  copied %d file(s) and %d document record(s) from %s. Nothing there "
                     u"was moved or deleted.\n" % (time.strftime("%Y-%m-%d %H:%M"),
                                                  report["copied"], report["records"], src))
    except (IOError, OSError):
        pass
    for k in ("_src", "_dest"):
        report.pop(k, None)
    return report


# ------------------------------------------------------------------ status

def status():
    path, src, how = resolve()
    try:
        key, kind, root = install()
    except ValueError:
        key, kind, root = "", "unknown", ""
    return {
        "chosen": path is not None,
        "folder": path,
        "decided_by": src,
        "how": how,
        "install": {"key": key, "kind": kind, "project": root, "skill": SKILL},
        "suggested": {"project": os.path.join(root, TOP)},
        "existing_work": existing_work(exclude=path),
        "locations_file": locations_file() if root else None,
    }


def _say_work(w):
    bits = []
    if w["facts"]:
        bits.append("a facts ledger")
    if w["jobs"]:
        bits.append("%d job%s" % (w["jobs"], "" if w["jobs"] == 1 else "s"))
    if w["loose_job_files"]:
        bits.append("working files for one earlier application")
    if w["documents"]:
        bits.append("%d finished document%s" % (w["documents"], "" if w["documents"] == 1 else "s"))
    if w["about_files"]:
        bits.append("%d file%s about the person" % (w["about_files"], "" if w["about_files"] == 1 else "s"))
    return ", ".join(bits)


def print_status(st):
    print("Task workspace: %s" % st["install"]["project"])
    if not st["chosen"]:
        print(not_chosen_message())
        return
    print("The person's files: %s" % st["folder"])
    print("  decided by: %s" % st["decided_by"])
    print("  layout: %s; %s; %s; %s" % (ABOUT, RECORD, JOBS, DOCUMENTS))
    print("Older folders are not searched or imported. Existing outputs are not source material without an explicit user request.")


# ------------------------------------------------------------------ one job each

#: `JOBS`, defined at the top, holds one working folder per advertisement. What belongs
#: to the person is reused only when explicitly requested.

#: A job id is a folder name, so it is held to letters, digits and hyphens. Anything
#: else, a slash or a `..` above all, would let a typo name a folder outside `jobs/`.
_JOB_ID_CHARS = "abcdefghijklmnopqrstuvwxyz0123456789-"


class NoSuchJob(Exception):
    """A job id that names no folder under `jobs/`. The message says what does exist."""


def valid_job_id(job_id):
    """True when `job_id` is safe to use as one folder name under `jobs/`."""
    return bool(job_id) and job_id[0] != "-" and all(c in _JOB_ID_CHARS for c in job_id)


def jobs_root():
    """`<their folder>/jobs`, created."""
    return sub(JOBS)


def known_jobs():
    """Every job id with a folder and a `job.json`, sorted."""
    root = os.path.join(data_dir(), JOBS)
    try:
        names = os.listdir(root)
    except OSError:
        return []
    return sorted(n for n in names if valid_job_id(n)
                  and os.path.isfile(os.path.join(root, n, "job.json")))


def find_job(given):
    """The one job id `given` means: an exact id, or the start of exactly one id.

    A person, or an assistant, will write `acme` for `acme-data-analyst-2026-09`, and
    refusing that helps nobody. Two jobs starting the same way is not guessed at: it
    is refused with both names, because working on the wrong application writes one
    employer's answers into another's folder.
    """
    given = (given or "").strip().lower()
    ids = known_jobs()
    if given in ids:
        return given
    hits = [i for i in ids if given and i.startswith(given)]
    if len(hits) == 1:
        return hits[0]
    if not ids:
        raise NoSuchJob("there are no jobs yet, so %r names nothing. Start one with "
                        "%s scripts/jobs.py new --role \"<title>\" --employer "
                        "\"<employer>\"." % (given, PY))
    if hits:
        raise NoSuchJob("%r could be any of %s. Use the whole id."
                        % (given, ", ".join(hits)))
    raise NoSuchJob("no job called %r. The jobs are: %s." % (given, ", ".join(ids)))


def job_dir(job_id):
    """`jobs/<id>/` for a job that exists. Raises NoSuchJob for one that does not.

    It is never created here. A job folder is made by `jobs.py new`, which also
    writes its record, so a folder that exists always has a `job.json` saying what
    it is for.
    """
    root = data_dir()
    folder = os.path.join(root, JOBS, find_job(job_id))
    if not _within(folder, root):
        raise NoSuchJob("The job folder resolves outside the data root; no substitute was used.")
    return folder


def job_file(job_id):
    """The `job.json` for one job."""
    return os.path.join(job_dir(job_id), "job.json")


def job_ad_dir(job_id):
    """Where the advertisement and its job pack are kept, verbatim, created."""
    path = os.path.join(job_dir(job_id), "ad")
    os.makedirs(path, exist_ok=True)
    return path


def job_documents_dir(job_id):
    """`4 Finished documents/<Employer - Role>/`, created.

    The name is read from the job's own record, where it was fixed when the job was
    made, so correcting a typo in the role later does not split one application's
    documents across two folders.
    """
    import json
    jid = find_job(job_id)
    name = jid
    try:
        with io.open(job_file(jid), encoding="utf-8") as fh:
            name = json.load(fh).get("documents_folder") or jid
    except (IOError, OSError, ValueError):
        pass
    root = documents_dir()
    path = os.path.join(root, name)
    if not _within(path, root):
        raise NoSuchJob("The job's document folder resolves outside the data root; no substitute was used.")
    os.makedirs(path, exist_ok=True)
    return path


#: What each one-path flag prints. Nothing else is printed with these, so they can
#: be used as `--facts "$(python3 scripts/paths.py --facts)"`.
_ONE_PATH = {
    "--data": lambda: data_dir(),
    "--facts": lambda: facts_file(),
    "--answers": lambda: answers_file(),
    "--documents": lambda: documents_dir(),
    "--cv-source": lambda: cv_source_dir(),
    "--about": lambda: cv_source_dir(),
    "--record": lambda: record_dir(),
    "--jobs": lambda: jobs_root(),
}

#: The same, for one job. Each needs `--job <id>` alongside it.
_JOB_PATH = {
    "--facts": facts_file,
    "--answers": answers_file,
    "--job-dir": job_dir,
    "--job-ad": job_ad_dir,
    "--job-documents": job_documents_dir,
    "--job-file": job_file,
}


def _usage():
    return ("usage: paths.py --status [--json]\n"
            "       paths.py --choose project|home|<folder> [--bring <folder>] [--user-instruction <request>]\n"
            "       paths.py [--data|--facts|--answers|--documents|--about|--record|--jobs]\n"
            "       paths.py --job <id> [--job-dir|--job-ad|--job-documents|--job-file|--facts|--answers]\n"
            "  no arguments : where everything goes\n"
            "  a flag       : that one path, on its own line, and nothing else\n")


def _value(argv, flag):
    i = argv.index(flag)
    if i + 1 >= len(argv) or argv[i + 1].startswith("--"):
        return None, argv
    return argv[i + 1], argv[:i] + argv[i + 2:]


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)

    if "-h" in argv or "--help" in argv:
        sys.stdout.write(_usage())
        return 0

    if "--status" in argv:
        st = status()
        if "--json" in argv:
            print(json.dumps(st, indent=2, ensure_ascii=False))
        else:
            print_status(st)
        return 0

    if "--choose" in argv:
        target, rest = _value(argv, "--choose")
        if not target:
            sys.stderr.write("paths.py: --choose needs project, home, or a whole folder path.\n")
            return 2
        user_instruction = None
        if "--user-instruction" in rest:
            user_instruction, rest = _value(rest, "--user-instruction")
            if not user_instruction:
                sys.stderr.write("paths.py: --user-instruction needs the user's exact instruction.\n")
                return 2
        bring_from = None
        if "--bring" in rest:
            bring_from, rest = _value(rest, "--bring")
            if not bring_from:
                sys.stderr.write("paths.py: --bring needs the folder to copy from.\n")
                return 2
        if rest:
            sys.stderr.write("paths.py: not understood with --choose: %s\n" % " ".join(rest))
            return 2
        try:
            r = choose(target, bring_from, user_instruction)
        except ValueError as e:
            sys.stderr.write("paths.py: %s\n" % e)
            return 5
        print("chose %s" % r["folder"])
        print("  for    : %s" % ("the project %s" % install()[2] if r["kind"] == "project"
                                 else "this whole computer"))
        if r["was"] and not _same(r["was"], r["folder"]):
            print("  before : %s, left exactly as it was" % r["was"])
        print("  made   : %s, %s, %s, %s, README.txt, and a .gitignore that keeps all of it "
              "out of git" % (ABOUT, RECORD, JOBS, DOCUMENTS))
        b = r["brought"]
        if b:
            print("  brought: %d file%s and %d document record%s from %s"
                  % (b["copied"], "" if b["copied"] == 1 else "s", b["records"],
                     "" if b["records"] == 1 else "s", b["from"]))
            if b["kept"]:
                print("  kept   : already here, so not copied: %s" % _some(b["kept"]))
            if b["failed"]:
                print("  FAILED : could not be copied: %s" % _some(b["failed"]))
            if b["left"]:
                print("  left   : not Resu Studio's, so not copied: %s" % _some(b["left"]))
            print("  nothing in %s was moved or deleted." % b["from"])
        return 0

    if "--job" in argv:
        given, rest = _value(argv, "--job")
        if not given:
            sys.stderr.write("paths.py: --job needs a job id after it. %s scripts/jobs.py "
                             "list shows them.\n" % PY)
            return 2
        flags = [a for a in rest if a in _JOB_PATH] or ["--job-dir"]
        stray = [a for a in rest if a not in _JOB_PATH]
        if stray:
            sys.stderr.write("paths.py: with --job, only %s can be asked for, not %s.\n"
                             % (" ".join(sorted(_JOB_PATH)), " ".join(stray)))
            return 2
        try:
            sys.stdout.write(_JOB_PATH[flags[0]](given) + "\n")
        except NoSuchJob as e:
            sys.stderr.write("paths.py: %s\n" % e)
            return 3
        return 0

    for arg in argv:
        if arg in _ONE_PATH:
            sys.stdout.write(_ONE_PATH[arg]() + "\n")
            return 0
        if arg in _JOB_PATH:
            sys.stderr.write("paths.py: %s is for one job, so it needs --job <id> "
                             "beside it.\n" % arg)
            return 2
        sys.stderr.write("paths.py: unknown option %s.\n%s" % (arg, _usage()))
        return 2

    path, src, how = resolve()
    if path is None:
        print_status(status())
        return NOT_CHOSEN
    print("The person's folder")
    print("  %s" % path)
    print("  decided by: %s" % src)
    print()
    for label, name in (("about them", ABOUT), ("their record", RECORD), ("jobs", JOBS),
                        ("finished", DOCUMENTS)):
        print("  %-12s: %s" % (label, os.path.join(path, name)))
    print("  %d job%s so far" % (len(known_jobs()), "" if len(known_jobs()) == 1 else "s"))
    print()
    print("  For a command line, one path and nothing else:")
    print("    %s scripts/paths.py --job <id> --facts" % PY)
    return 0


if __name__ == "__main__":
    sys.exit(main())
