"""Where this person's own files live, and why that is not inside the skill.

A plugin is not updated in place. An update puts down a fresh copy of the plugin
folder and throws the old one away a couple of weeks later, so anything a person
built up inside it goes with it: their history, their facts ledger, every finished
CV. They would lose years of their own work to a routine update and nothing on
screen would connect the two events.

So the skill asks where its files go rather than assuming it is allowed to keep
them inside itself. In order:

    1. a pointer file, one line holding a folder. Read from two places:
           ~/.resu-studio/location   the stable one, outside the plugin, so an
                                     update cannot take the pointer with it.
           <skill>/data-location.txt the original one. Still honoured, and copied
                                     out to the stable place the first time it is
                                     used, so the next update cannot lose it.
       A human wrote this, so it wins over anything the host guessed.
    2. CLAUDE_PLUGIN_DATA or PLUGIN_DATA
                            the host's own folder for data that outlives an update.
                            Claude sets the first when this is installed as a
                            plugin; PLUGIN_DATA is the name the Agent Plugins
                            standard uses. Used when no pointer was written.
    3. ~/.resu-studio       last resort, and still outside the plugin, so a bare
                            checkout keeps this person's work through an update.
    4. <skill>/data         only when a home folder cannot be made at all. Says so
                            loudly, because it is the one answer an update deletes.

A pointer is checked before it is believed. When the scripts run on Linux or a Mac,
a Windows path such as `D:\\CVs`, or anything holding a backslash, is not a path
they can see: it would be created as one directory with backslashes in its name, in
some working directory, and every finished document would go there and never be
found. It is refused, by name, with what to write instead. When the scripts run on
Windows itself, which is where Codex, Copilot, Cursor and Gemini CLI run for a
Windows user, a drive letter is exactly the right way to write it and is accepted.

Anybody who used this skill before it stopped keeping files inside itself has their
whole history sitting in `<skill>/data`: their facts ledger, their answers, their
documents list and every PDF they printed. Resolving to a new folder on its own
would show them an empty history and quietly rebuild a ledger they already have,
and a fact they told the assistant rather than wrote on a CV has nothing to be rebuilt
from. So the first time the new folder is used, the old one is copied into it. See
`_bring_forward`.

Nothing here deletes or moves anything. It resolves a folder, creates it, and
copies into it.

    python3 scripts/paths.py            where everything goes, and why
    python3 scripts/paths.py --facts    just the path, for a command line
    python3 scripts/paths.py --job <id> [--job-dir|--job-ad|--job-documents|--job-file]
                                        one job's folder, see scripts/jobs.py
"""

import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)

#: True when Python itself is running on Windows. Then `D:\\CVs` is a real folder
#: this process can open, and refusing it would lock a Windows user out of choosing
#: where their own files go.
ON_WINDOWS = os.name == "nt"

#: How to name Python in a message a person or an agent will copy. Windows installs
#: it as `python` or `py`; `python3` is usually missing there.
PY = "python" if ON_WINDOWS else "python3"

#: The host's own data folder, in the order they are trusted. CLAUDE_PLUGIN_DATA is
#: what Claude sets for an installed plugin; PLUGIN_DATA is the Agent Plugins name.
DATA_ENV = ("CLAUDE_PLUGIN_DATA", "PLUGIN_DATA")


def utf8_output():
    """Make printing a name like Zoë safe on Windows. Harmless everywhere else.

    An agent reads a script's output through a pipe, and on Windows a pipe uses the
    old code page, so the first accented letter or typographic dash in somebody's CV
    stops the script with UnicodeEncodeError halfway through a render.
    """
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass


if ON_WINDOWS:
    utf8_output()


def _host_data():
    """(variable name, value) for the first host data folder that is set, or (None, None)."""
    for name in DATA_ENV:
        value = os.environ.get(name)
        if value:
            return name, value
    return None, None

#: The folder finished documents land in. Named for what is in it rather than for
#: what the code calls it, and prefixed so it sorts above everything else: somebody
#: who has never opened a terminal should find their CV first thing.
DOCUMENTS = "_Your Documents Are Here"

#: The pointer inside the plugin. Kept working because people were told to write it,
#: but an update deletes it, so it is copied out to STABLE_POINTER when it is used.
_POINTER = os.path.join(SKILL, "data-location.txt")

#: Outside the plugin, and therefore still there after an update.
HOME_DIR = os.path.join(os.path.expanduser("~"), ".resu-studio")
STABLE_POINTER = os.path.join(HOME_DIR, "location")

#: The last resort of all, inside the skill. An update replaces this folder, and it
#: is also where everybody's files used to live, so it is what is copied forward.
INSIDE = os.path.join(SKILL, "data")

#: Dropped in the person's folder once the old one has been copied into it, so this
#: happens once. Hidden, because the folder is meant to be opened by somebody who
#: has never used a terminal and the first thing in it should be their documents.
MARKER = ".migrated-from-plugin"

#: Set while a copy is running. `documents.py` imports `paths`, and when paths.py is
#: the script being run that import makes a second, separate copy of this module with
#: its own idea of what has already happened. A name in the environment is the one
#: guard both copies can see.
_BUSY = "RESU_STUDIO_BRINGING_FORWARD"

_WARNED = False
_RESOLVED = None      # resolve() is asked many times per run and cannot change
                      # inside one; caching it also keeps a complaint about a bad
                      # pointer to one line instead of one per call.
_BROUGHT_FORWARD = False


def _usable(path):
    """True when we can actually write there. Asked by permission, not by probing.

    An earlier version wrote a test file and deleted it, which reported "not
    writable" on any filesystem that allows writing but not deleting, and left a
    stray file behind every time it was wrong.
    """
    try:
        os.makedirs(path, exist_ok=True)
        return os.access(path, os.W_OK)
    except OSError:
        return False


def _mount_roots():
    """Every `*/mnt/*` style folder on this session that actually exists.

    A Windows folder reaches a Linux session through a mount, so when somebody
    names `D:\\resu-plugin` the folder itself is usually right here under a
    different name, and saying so is more use than saying no.
    """
    import glob
    home = os.path.expanduser("~")
    roots = []
    for pattern in (os.path.join(home, "mnt"), "/mnt", "/home/*/mnt",
                    "/Users/*/mnt", "/sessions/*/mnt", "/workspace/*/mnt"):
        for hit in glob.glob(pattern):
            if os.path.isdir(hit) and hit not in roots:
                roots.append(hit)
    return roots


def _mounted_equivalent(raw):
    """A session path holding the same folder name, or None. Best effort only."""
    leaf = raw.replace("\\", "/").rstrip("/").rsplit("/", 1)[-1].strip()
    if not leaf or ":" in leaf:
        return None
    for root in _mount_roots():
        for depth in (0, 1):
            try:
                if depth == 0:
                    here = [root]
                else:
                    here = [os.path.join(root, n) for n in os.listdir(root)
                            if os.path.isdir(os.path.join(root, n))]
            except OSError:
                continue
            for folder in here:
                try:
                    for name in os.listdir(folder):
                        if name.lower() == leaf.lower() \
                                and os.path.isdir(os.path.join(folder, name)):
                            return os.path.join(folder, name)
                except OSError:
                    continue
    return None


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
        hint = _mounted_equivalent(raw)
        msg = ("the pointer%s names %s, which is a Windows path. This session "
               "cannot see drive letters or backslashes, and using it as written "
               "would make one folder whose name contains the backslashes and put "
               "every document in it. Write the path as this session sees it: it "
               "starts with a / and has no backslashes, usually something like "
               "/home/<you>/mnt/<folder>." % (label, raw))
        if hint:
            msg += " This session can see %s, which looks like the same folder." % hint
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


def _first_line(path):
    """The first meaningful line of a pointer file, or None. `#` is a comment."""
    try:
        with io.open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line and not line.startswith("#"):
                    return line
    except (IOError, OSError, UnicodeDecodeError):
        pass
    return None


def _pointers():
    """Every pointer that exists, stable one first, as (label, file, raw line)."""
    found = []
    for label, fp in (("~/.resu-studio/location", STABLE_POINTER),
                      ("data-location.txt (inside the skill)", _POINTER)):
        raw = _first_line(fp)
        if raw:
            found.append((label, fp, raw))
    return found


def _copy_pointer_out(raw):
    """Put the in-plugin pointer somewhere an update cannot reach it."""
    try:
        os.makedirs(HOME_DIR, exist_ok=True)
        if _first_line(STABLE_POINTER) == raw.strip():
            return False
        with io.open(STABLE_POINTER, "w", encoding="utf-8", newline="") as fh:
            fh.write(
                u"# Written by resu-studio from data-location.txt inside the plugin,\n"
                u"# so that a plugin update cannot take the pointer with it.\n"
                u"%s\n" % raw.strip())
        return True
    except (IOError, OSError):
        return False


def resolve(force=False):
    """(folder, where_it_came_from, survives_an_update)."""
    global _RESOLVED
    if _RESOLVED is not None and not force:
        return _RESOLVED[:3]
    _RESOLVED = _resolve_once()
    # Cached before the copy runs, because the copy asks documents.py where the
    # ledger is and documents.py asks this back. Answering from the cache is what
    # keeps that from going round in a circle.
    _bring_forward(_RESOLVED[0], _RESOLVED[3])
    return _RESOLVED[:3]


def _resolve_once():
    """(folder, where_it_came_from, survives_an_update, which_of_the_four)."""
    env_name, env = _host_data()

    for label, _fp, raw in _pointers():
        path, complaint = check_pointer_text(raw, label)
        if complaint:
            sys.stderr.write("resu-studio: %s\n" % complaint)
            continue
        if not _usable(path):
            sys.stderr.write(
                "resu-studio: %s names %s, which cannot be written to. Trying the "
                "next place.\n" % (label, path))
            continue
        if label.startswith("data-location.txt"):
            _copy_pointer_out(raw)
        return path, label, True, "pointer"

    if env:
        # The host made this folder up, and may not have created it yet, so its
        # parent is not required to exist. The rest of the checks still apply: a
        # backslash in here would build the same junk folder as anywhere else.
        path, complaint = check_pointer_text(env, env_name, require_parent=False)
        if complaint:
            sys.stderr.write("resu-studio: %s\n" % complaint)
        elif _usable(path):
            return path, env_name, True, "env"

    if _usable(HOME_DIR):
        return HOME_DIR, "~/.resu-studio (nothing else was named)", True, "home"

    return INSIDE, "inside the skill (nowhere else could be created)", False, "inside"


def _holds_files(root):
    """True when there is at least one file anywhere under `root`.

    An empty folder left over from an install is not somebody's history, and
    announcing a copy of nothing is noise in the middle of a render.
    """
    try:
        for _here, _dirs, files in os.walk(root):
            if files:
                return True
    except OSError:
        pass
    return False


def _copy_tree(old, dest, skip):
    """Copy every file under `old` into `dest`. Returns (copied, kept, failed).

    Nothing is moved and nothing is deleted: `old` is left exactly as it was, so a
    copy that goes wrong halfway costs nobody anything. Nothing already in `dest`
    is written over either, because the file there is the newer one by definition,
    and the name of every file that was not copied for that reason comes back in
    `kept` so it can be said out loud rather than guessed at.
    """
    import shutil
    copied, kept, failed = 0, [], []
    for here, _dirs, files in os.walk(old):
        rel = os.path.relpath(here, old)
        target = dest if rel == os.curdir else os.path.join(dest, rel)
        try:
            os.makedirs(target, exist_ok=True)
        except OSError:
            failed.extend(f if rel == os.curdir else os.path.join(rel, f)
                          for f in files)
            continue
        for name in files:
            relname = name if rel == os.curdir else os.path.join(rel, name)
            if relname in skip:
                continue
            try:
                if os.path.exists(os.path.join(target, name)):
                    kept.append(relname)
                    continue
                shutil.copy2(os.path.join(here, name), os.path.join(target, name))
                copied += 1
            except (IOError, OSError, shutil.Error):
                failed.append(relname)
    return copied, kept, failed


def _repoint(records, old, dest):
    """Point records at the copy of the file rather than at the original. Returns how many.

    Every record keeps the whole path of the document it describes, and every one of
    those paths is inside the folder an update is about to delete. Left alone, a
    brought forward history lists every document somebody ever printed as moved or
    deleted, which is the opposite of what just happened to it.
    """
    n = 0
    old = os.path.abspath(old)
    for rec in records.values():
        if not isinstance(rec, dict):
            continue
        if not rec.get("path"):
            continue
        was = os.path.abspath(rec["path"])
        if was != old and not was.startswith(old + os.sep):
            continue
        now = os.path.join(dest, os.path.relpath(was, old))
        if os.path.exists(now):
            rec["path"] = now
            n += 1
    return n


def _documents():
    """The documents module, or None when it cannot be loaded.

    None is survivable: the ledger is then copied like any other file, which is
    right when the destination has none and safe when it has one, and only the
    merging of two real ledgers is lost.
    """
    try:
        if HERE not in sys.path:
            sys.path.insert(0, HERE)
        import documents
        return documents
    except Exception:                                         # noqa: BLE001
        return None


def _merge_ledger(documents, old, dest):
    """Bring the old documents list into the new one. Returns (brought, repointed).

    Both files can hold real history, so neither is chosen over the other: every
    record from both is kept. Where the same document is in both, the one already in
    the destination stays, on the same reasoning as every other file here.

    documents.py does the reading and the writing. The shape of a record and the way
    it is keyed are its business, and a second reader here would be wrong the first
    time either of them changed.
    """
    old_file = os.path.join(old, documents.LEDGER)
    if not os.path.isfile(old_file):
        return 0, 0
    was = documents.load_ledger(old_file)
    if not was:
        return 0, 0
    repointed = _repoint(was, old, dest)
    here = documents.load_ledger(os.path.join(dest, documents.LEDGER))
    brought = [k for k in was if k not in here]
    if not brought:
        return 0, 0
    merged = dict(was)
    merged.update(here)          # a key in both: the destination's record wins
    documents.save_ledger(merged, os.path.join(dest, documents.LEDGER))
    return len(brought), repointed


def _some(names, limit=6):
    """A few names, said plainly, with a count for the rest."""
    shown = ", ".join(sorted(names)[:limit])
    if len(names) > limit:
        shown += " and %d more" % (len(names) - limit)
    return shown


def _bring_forward(dest, kind):
    """Copy the old in-plugin folder into the person's folder, once, and say so.

    This runs for the folder nobody named (`~/.resu-studio`) and for a folder
    somebody pointed at. It does not run for the host's data folder, because that was
    already preferred over the in-plugin folder before any of this changed, so
    nobody's files were ever in the old place while that was set.

    It can never stop a render. Everything it does is somebody's history and none of
    it is this afternoon's document, so any failure at all is one line and carry on.
    """
    global _BROUGHT_FORWARD
    if _BROUGHT_FORWARD or os.environ.get(_BUSY):
        return
    _BROUGHT_FORWARD = True
    try:
        _bring_forward_once(dest, kind)
    except Exception as exc:                                  # noqa: BLE001
        sys.stderr.write(
            "resu-studio: could not copy your earlier work out of %s (%s). Nothing "
            "there was changed, and it is all still where it was.\n" % (INSIDE, exc))


def _bring_forward_once(dest, kind):
    if kind not in ("home", "pointer"):
        return
    if not os.path.isdir(INSIDE):
        return
    # Somebody can point at the old folder, or at a folder inside it. Copying a
    # folder into itself either does nothing or never stops, and neither is a thing
    # to do while somebody is waiting for a document.
    old_at, dest_at = os.path.abspath(INSIDE), os.path.abspath(dest)
    if dest_at == old_at or dest_at.startswith(old_at + os.sep):
        return
    if os.path.exists(os.path.join(dest, MARKER)):
        return
    if not _holds_files(INSIDE):
        return

    os.environ[_BUSY] = "1"
    try:
        docs = _documents()
        skip = {MARKER}
        if docs is not None:
            skip.add(docs.LEDGER)   # merged below rather than copied over
        copied, kept, failed = _copy_tree(INSIDE, dest, skip)
        records = repointed = 0
        if docs is not None:
            try:
                records, repointed = _merge_ledger(docs, INSIDE, dest)
            except Exception as exc:                          # noqa: BLE001
                failed.append("%s (%s)" % (docs.LEDGER, exc))
    finally:
        os.environ.pop(_BUSY, None)

    if copied or records:
        lines = ["resu-studio: your earlier work was inside the plugin, where an "
                 "update deletes it, so it has been copied out.",
                 "  from %s" % INSIDE,
                 "  to   %s" % dest,
                 "  %d file(s) copied%s."
                 % (copied, ", and %d entry(s) in your documents list" % records
                    if records else "")]
    else:
        lines = ["resu-studio: there is an old folder inside the plugin at %s, and "
                 "everything in it is already in %s, so nothing was copied."
                 % (INSIDE, dest)]
    if kept:
        lines.append("  already here, so the copy was not made: %s" % _some(kept))
    if failed:
        lines.append("  could not be copied, and is still in the old folder: %s"
                     % _some(failed))
    lines.append("  the old folder was left exactly as it was. Nothing was moved or "
                 "deleted.")
    sys.stderr.write("\n".join(lines) + "\n")

    _write_marker(dest, copied, kept, failed, records, repointed)


def _write_marker(dest, copied, kept, failed, records, repointed):
    """The note that stops this happening twice. Written last, and readable.

    Last, because until the copy has been made there is nothing to remember, and
    readable, because somebody who finds two copies of their CV deserves to be able
    to open one file and see why.
    """
    import time
    try:
        with io.open(os.path.join(dest, MARKER), "w",
                     encoding="utf-8", newline="") as fh:
            fh.write(u"resu-studio copied this person's earlier work into this "
                     u"folder on %s.\n" % time.strftime("%Y-%m-%d %H:%M"))
            fh.write(u"It came from %s, inside the plugin, which a plugin update "
                     u"deletes.\n" % INSIDE)
            fh.write(u"%d file(s) were copied, and %d entry(s) in the documents "
                     u"list.\n" % (copied, records))
            if repointed:
                fh.write(u"%d of those entries were pointed at the copy of the "
                         u"document in this folder.\n" % repointed)
            fh.write(u"Nothing there was moved or deleted.\n")
            if kept:
                fh.write(u"Already here, so not copied: %s\n" % _some(kept, 200))
            if failed:
                fh.write(u"Could not be copied: %s\n" % _some(failed, 200))
            fh.write(u"This file is what stops that copy being made a second time. "
                     u"Deleting it makes it happen again, which is harmless: "
                     u"nothing here would be written over.\n")
    except (IOError, OSError) as exc:
        sys.stderr.write(
            "resu-studio: the copy was made but the note saying so could not be "
            "written to %s (%s), so this will be checked again next time. Nothing "
            "already there will be written over.\n" % (dest, exc))


def _warn_once(path):
    """One line, once, when the resolved folder will not survive an update.

    One line because it prints in the middle of a render and a paragraph there is
    noise somebody learns to scroll past.
    """
    global _WARNED
    if _WARNED:
        return
    _WARNED = True
    sys.stderr.write(
        "resu-studio: WARNING your files are in %s, inside the plugin, and a plugin "
        "update deletes it. Run %s scripts/paths.py to move them.\n" % (path, PY))


def data_dir():
    """The person's own folder. Created if it is not there yet."""
    path, _src, _safe = resolve()
    os.makedirs(path, exist_ok=True)
    return path


def documents_dir():
    """Where finished CVs and letters land."""
    base, _src, safe = resolve()
    if not safe:
        _warn_once(base)
    path = os.path.join(base, DOCUMENTS)
    os.makedirs(path, exist_ok=True)
    return path


def sub(*parts):
    """A named folder inside the person's own folder, created."""
    path = os.path.join(data_dir(), *parts)
    os.makedirs(path, exist_ok=True)
    return path


def facts_file():
    """The reusable history. One per person, read by every advertisement."""
    base, _src, safe = resolve()
    if not safe:
        _warn_once(base)
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, "facts.md")


def answers_file():
    """What was asked and answered, kept beside the history."""
    return os.path.join(data_dir(), "answers.md")


def documents_ledger():
    """The small record saying which advertisement each document was for."""
    return os.path.join(data_dir(), "documents.json")


def cv_source_dir():
    """The CV as it arrived, kept exactly as it was handed over.

    Created, like every other folder here. The very first instruction anybody is
    given copies their advertisement into this folder, and a path that is handed
    out but not made turns that first command into `cp: cannot create regular
    file ... No such file or directory` before the skill has done anything at all.
    """
    return sub("cv-source")


# ------------------------------------------------------------------ one job each

#: The folder holding one working folder per advertisement. Everything that belongs
#: to a single application lives in its own folder under here: the advertisement as
#: it arrived, the asks ledger, the scorecard, the proposals, the decisions, the
#: tailored CV and the letter. What belongs to the person, `facts.md`, `answers.md`
#: and `cv-source/`, stays where it always was, so every job reads the same history.
JOBS = "jobs"

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
    return os.path.join(data_dir(), JOBS, find_job(job_id))


def job_file(job_id):
    """The `job.json` for one job."""
    return os.path.join(job_dir(job_id), "job.json")


def job_ad_dir(job_id):
    """Where the advertisement and its job pack are kept, verbatim, created."""
    path = os.path.join(job_dir(job_id), "ad")
    os.makedirs(path, exist_ok=True)
    return path


def job_documents_dir(job_id):
    """`_Your Documents Are Here/<Employer - Role>/`, created.

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
    path = os.path.join(documents_dir(), name)
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
    "--jobs": lambda: jobs_root(),
}

#: The same, for one job. Each needs `--job <id>` alongside it.
_JOB_PATH = {
    "--job-dir": job_dir,
    "--job-ad": job_ad_dir,
    "--job-documents": job_documents_dir,
    "--job-file": job_file,
}


def _usage():
    return ("usage: paths.py [--data|--facts|--answers|--documents|--cv-source|--jobs]\n"
            "       paths.py --job <id> [--job-dir|--job-ad|--job-documents|--job-file]\n"
            "  no arguments : where everything goes, and why\n"
            "  a flag       : that one path, on its own line, and nothing else\n"
            "  --job <id>   : with no other flag, the job's own folder\n")


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)

    if "--job" in argv:
        i = argv.index("--job")
        if i + 1 >= len(argv) or argv[i + 1].startswith("-"):
            sys.stderr.write("paths.py: --job needs a job id after it. %s scripts/jobs.py "
                             "list shows them.\n" % PY)
            return 2
        given = argv[i + 1]
        rest = argv[:i] + argv[i + 2:]
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
        if arg in ("-h", "--help"):
            sys.stdout.write(_usage())
            return 0
        if arg.startswith("-"):
            sys.stderr.write("paths.py: unknown option %s. Known: %s --job %s\n"
                             % (arg, " ".join(sorted(_ONE_PATH)),
                                " ".join(sorted(_JOB_PATH))))
            return 2

    path, src, safe = resolve()
    print("The person's folder")
    print("  %s" % path)
    print("  chosen by: %s" % src)
    if safe:
        print("  a plugin update will not touch it.")
    else:
        print("  WARNING: this is inside the skill. A plugin update replaces the")
        print("  skill folder, so anything here goes with it. To move it, put one")
        print("  line, the folder you want, in:")
        print("    %s" % STABLE_POINTER)

    others = [lbl for lbl, _fp, _raw in _pointers() if lbl != src]
    if others:
        print("  also present, not used: %s" % ", ".join(others))
    env_name, env = _host_data()
    if env and src != env_name:
        print("  %s is set to %s and was not used: a pointer file "
              "is a person's own choice and comes first." % (env_name, env))

    print()
    print("  documents : %s" % os.path.join(path, DOCUMENTS))
    print("  facts     : %s" % os.path.join(path, "facts.md"))
    print("  answers   : %s" % os.path.join(path, "answers.md"))
    print("  the CV as it arrived : %s" % os.path.join(path, "cv-source"))
    print("  jobs      : %s  (%d so far)" % (os.path.join(path, JOBS), len(known_jobs())))
    print()
    print("  For a command line, one path and nothing else:")
    print("    %s scripts/paths.py --facts" % PY)
    print("    %s" % " ".join(sorted(_ONE_PATH)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
