"""Where this person's own files live, and how that is decided.

A CV, a facts ledger, every job ad and every finished document is private. None of it
belongs inside the plugin, where an update deletes it, and none of it belongs anywhere
the person did not choose. The skill used to settle this on its own: one folder per
computer, `~/.resu-studio`, shared by every install. That kept files safe from updates,
and it also meant an install made inside one project quietly found an application
somebody had started from a different project, and said so as if it were expected.

So the folder is now chosen by the person, once per install, and remembered:

    1. <skill>/data-location.txt   one line, a folder, written inside this install.
    2. this install's choice       recorded in <config>/locations.json by
                                   `paths.py --choose`. <config> is ~/.resu-studio,
                                   or $RESU_STUDIO_CONFIG. The key is the project the
                                   skill is installed in, or `~` for an install that
                                   serves the whole computer.
    3. CLAUDE_PLUGIN_DATA or PLUGIN_DATA
                                   the host's own folder for data that outlives an
                                   update. The host chose it, so nobody is asked.
    4. nothing                     not chosen. Every script that needs the folder
                                   stops with exit 6 and one sentence: ask the person,
                                   using `paths.py --status`, then `paths.py --choose`.
                                   Nothing is created, and no other folder is used in
                                   the meantime, however much work it holds.

An older folder, `~/.resu-studio`, the folder an old `~/.resu-studio/location` pointer
named, or the old `data/` inside the plugin, is never used on its own any more. It is
listed by `--status` as work that already exists, and `--choose ... --bring <folder>`
copies it in when the person says so.

Inside the chosen folder:

    Resu - CV Builder/
      README.txt, .gitignore     says what this is; ignores everything in it for git
      1 About me/                the CV as it arrived, the CV as markdown, links.md
      2 My record/               facts.md, answers.md: reused by every job
      3 Jobs/<job id>/           one folder per advertisement, see scripts/jobs.py
      4 Finished documents/      Resu Desk, and a folder of documents per job
      .resu/                     documents.json and the notes the scripts keep

The `.gitignore` holds one line, `*`, which tells git to ignore every file in the folder,
the `.gitignore` included. A person who keeps their CV folder inside a repository cannot
commit it by accident, and nobody's own `.gitignore` is edited to get that.

A folder is checked before it is believed. When the scripts run on Linux or a Mac, a
Windows path such as `D:\\CVs`, or anything holding a backslash, is refused with what to
write instead. On Windows itself a drive letter is the right way to write it.

Nothing here deletes or moves anything.

    python3 scripts/paths.py --status [--json]    chosen or not, and what already exists
    python3 scripts/paths.py --choose project|home|<folder> [--bring <folder>]
    python3 scripts/paths.py                      where everything goes
    python3 scripts/paths.py --facts              just the path, for a command line
    python3 scripts/paths.py --job <id> [--job-dir|--job-ad|--job-documents|--job-file]

Exit codes: 0 done, 2 wrong command line, 3 no such job, 5 could not write, 6 not chosen.
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

#: The host's own data folder, in the order they are trusted.
DATA_ENV = ("CLAUDE_PLUGIN_DATA", "PLUGIN_DATA")

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

#: The pointer inside this install. An update replaces it with the install, which is
#: the point: it belongs to this install and nothing else.
_POINTER = os.path.join(SKILL, "data-location.txt")

#: The old per-computer folder and its pointer. Read only to offer them as existing work.
HOME_DIR = os.path.join(os.path.expanduser("~"), ".resu-studio")
STABLE_POINTER = os.path.join(HOME_DIR, "location")

#: Where everybody's files lived before they lived outside the plugin.
INSIDE = os.path.join(SKILL, "data")

#: The folders an agent installs skills into, inside a project.
_INSTALL_DIRS = (".agents", ".claude", ".codex", ".cursor", ".gemini", ".github")

README_TEXT = u"""Resu - CV Builder
=================

This folder holds your CV, your working history, the job ads you applied for and the
documents Resu Studio made for you. It is private and belongs to you.

  1 About me             your CV as you gave it, and any links you shared
  2 My record            everything learned about your working life, reused for every job
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


def _host_data():
    """(variable name, value) for the first host data folder that is set, or (None, None)."""
    for name in DATA_ENV:
        value = os.environ.get(name)
        if value:
            return name, value
    return None, None


_RESOLVED = None


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



def _some(names, limit=6):
    """A few names, said plainly, with a count for the rest."""
    names = list(names)
    shown = ", ".join(sorted(names)[:limit])
    if len(names) > limit:
        shown += " and %d more" % (len(names) - limit)
    return shown


# ------------------------------------------------------------------ which install is this

def config_dir():
    """Where the record of each install's choice is kept. Outside every install."""
    return os.environ.get("RESU_STUDIO_CONFIG") or HOME_DIR


def locations_file():
    return os.path.join(config_dir(), "locations.json")


def _same(a, b):
    return os.path.normcase(os.path.abspath(a)) == os.path.normcase(os.path.abspath(b))


def install():
    """(key, kind, project root or None) for the install this script belongs to.

    A skill installed into a project sits at `<project>/.agents/skills/resu-studio`, or
    under `.claude`, `.codex` and the rest. When that project is the home folder itself,
    it is an install for the whole computer, and so is anything else: a Claude plugin
    cache, a global skills folder, a checkout of the repository.
    """
    parts = os.path.abspath(SKILL).split(os.sep)
    for i in range(len(parts) - 2, 0, -1):
        if parts[i] in _INSTALL_DIRS and i + 1 < len(parts) and parts[i + 1] == "skills":
            root = os.sep.join(parts[:i]) or os.sep
            if ON_WINDOWS and len(parts[0]) == 2 and i == 1:
                root = parts[0] + os.sep
            if _same(root, os.path.expanduser("~")):
                break
            return os.path.normcase(os.path.abspath(root)), "project", root
    return "~", "computer", None


def _read_locations():
    try:
        with io.open(locations_file(), encoding="utf-8") as fh:
            data = json.load(fh)
            return data if isinstance(data, dict) else {}
    except (IOError, OSError, ValueError):
        return {}


def recorded_choice():
    """The folder recorded for this install, or None."""
    key, _kind, _root = install()
    entry = _read_locations().get(key)
    if isinstance(entry, dict):
        return entry.get("folder")
    return None


def suggested_folder(where):
    """The folder offered for `project` or `home`, or None when it does not apply."""
    _key, kind, root = install()
    if where == "project":
        return os.path.join(root, TOP) if kind == "project" else None
    if where == "home":
        return os.path.join(os.path.expanduser("~"), TOP)
    return None


# ------------------------------------------------------------------ resolving

def resolve(force=False):
    """(folder or None, where_it_came_from, how). `how` is pointer, chosen, env or none."""
    global _RESOLVED
    if _RESOLVED is None or force:
        _RESOLVED = _resolve_once()
    return _RESOLVED


def _resolve_once():
    raw = _first_line(_POINTER)
    if raw:
        path, complaint = check_pointer_text(raw, "data-location.txt (inside the skill)")
        if complaint:
            sys.stderr.write("resu-studio: %s\n" % complaint)
        elif _usable(path):
            return path, "data-location.txt inside this install", "pointer"

    chosen = recorded_choice()
    if chosen:
        path, complaint = check_pointer_text(chosen, locations_file(), require_parent=False)
        if complaint:
            sys.stderr.write("resu-studio: %s\n" % complaint)
        elif _usable(path):
            return path, "chosen for this install", "chosen"
        else:
            sys.stderr.write("resu-studio: the folder chosen for this install, %s, cannot "
                             "be written to.\n" % chosen)

    env_name, env = _host_data()
    if env:
        path, complaint = check_pointer_text(env, env_name, require_parent=False)
        if complaint:
            sys.stderr.write("resu-studio: %s\n" % complaint)
        elif _usable(path):
            return path, env_name, "env"

    return None, "not chosen yet", "none"


def not_chosen_message():
    return ("resu-studio: nobody has chosen where this install keeps the person's files "
            "yet, so nothing was read or written. Run %s scripts/paths.py --status, tell "
            "the person what it found, ask where their files should live, then run "
            "%s scripts/paths.py --choose with their answer." % (PY, PY))


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
    os.makedirs(path, exist_ok=True)
    ensure_private(path)
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


def facts_file():
    """The reusable history. One per person, read by every advertisement."""
    return os.path.join(record_dir(), "facts.md")


def answers_file():
    """What was asked and answered, kept beside the history."""
    return os.path.join(record_dir(), "answers.md")


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
    """Every other folder on this computer holding Resu Studio work, as summaries."""
    seen, out = [], []

    def add(folder, label):
        if not folder:
            return
        folder = os.path.abspath(os.path.expanduser(folder))
        if any(_same(folder, s) for s in seen) or (exclude and _same(folder, exclude)):
            return
        seen.append(folder)
        w = work_in(folder)
        if w:
            w["found_as"] = label
            out.append(w)

    add(HOME_DIR, "the folder every install used to share")
    raw = _first_line(STABLE_POINTER)
    if raw:
        add(raw, "named by the old ~/.resu-studio/location pointer")
    add(INSIDE, "inside this install, where an update deletes it")
    add(suggested_folder("home"), "in your home folder")
    if suggested_folder("project"):
        add(suggested_folder("project"), "in this project")
    for key, entry in _read_locations().items():
        if isinstance(entry, dict):
            add(entry.get("folder"), "chosen by another install (%s)" % key)
    _name, env = _host_data()
    add(env, "the host's data folder")
    return out


# ------------------------------------------------------------------ choosing

def ensure_layout(path):
    for name in (ABOUT, RECORD, JOBS, DOCUMENTS, SYSTEM):
        os.makedirs(os.path.join(path, name), exist_ok=True)
    _PRIVATE_DONE.discard(path)
    ensure_private(path)


def choose(target, bring_from=None):
    """Record where this install keeps files, make the folder, and bring work in if asked.

    Returns a report dict. Raises ValueError with a sentence fit to show.
    """
    key, kind, root = install()
    if target == "project":
        if kind != "project":
            raise ValueError("this install is not inside a project, so there is no project "
                             "folder to choose. Choose home, or give a whole folder path.")
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

    try:
        os.makedirs(folder, exist_ok=True)
        ensure_layout(folder)
    except OSError as e:
        raise ValueError("%s could not be created (%s)." % (folder, e))

    locs = _read_locations()
    was = (locs.get(key) or {}).get("folder") if isinstance(locs.get(key), dict) else None
    import time
    locs[key] = {"folder": folder, "kind": kind, "skill": SKILL,
                 "chosen": time.strftime("%Y-%m-%d %H:%M")}
    try:
        os.makedirs(config_dir(), exist_ok=True)
        tmp = locations_file() + ".tmp"
        with io.open(tmp, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(locs, indent=2, ensure_ascii=False) + "\n")
        os.replace(tmp, locations_file())
    except OSError as e:
        raise ValueError("the choice could not be recorded in %s (%s)." % (locations_file(), e))

    global _RESOLVED
    _RESOLVED = None
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
    key, kind, root = install()
    return {
        "chosen": path is not None,
        "folder": path,
        "decided_by": src,
        "how": how,
        "install": {"key": key, "kind": kind, "project": root, "skill": SKILL},
        "suggested": {"project": suggested_folder("project"), "home": suggested_folder("home")},
        "existing_work": existing_work(exclude=path),
        "locations_file": locations_file(),
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
    inst = st["install"]
    print("This install")
    print("  %s" % inst["skill"])
    print("  %s" % ("inside the project %s" % inst["project"] if inst["kind"] == "project"
                    else "serves the whole computer"))
    print()
    if st["chosen"]:
        print("The person's files: %s" % st["folder"])
        print("  decided by: %s" % st["decided_by"])
    else:
        print("The person's files: NOT CHOSEN YET. Ask the person before doing anything else.")
        print()
        print("Folders to offer")
        if st["suggested"]["project"]:
            print("  project : %s" % st["suggested"]["project"])
        print("  home    : %s" % st["suggested"]["home"])
        print("  or any folder they name")
    if st["existing_work"]:
        print()
        print("Resu Studio work that already exists on this computer. Say where it is and "
              "ask\nwhether to bring it in (--bring), before using any of it:")
        for w in st["existing_work"]:
            print("  %s" % w["folder"])
            print("    %s: %s" % (w["found_as"], _say_work(w)))
    if not st["chosen"]:
        print()
        print("Then: %s scripts/paths.py --choose project|home|<folder> [--bring <folder>]" % PY)


# ------------------------------------------------------------------ one job each

#: `JOBS`, defined at the top, holds one working folder per advertisement. What belongs
#: to the person, `1 About me` and `2 My record`, is read by every job.

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
    "--about": lambda: cv_source_dir(),
    "--record": lambda: record_dir(),
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
    return ("usage: paths.py --status [--json]\n"
            "       paths.py --choose project|home|<folder> [--bring <folder>]\n"
            "       paths.py [--data|--facts|--answers|--documents|--about|--record|--jobs]\n"
            "       paths.py --job <id> [--job-dir|--job-ad|--job-documents|--job-file]\n"
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
            r = choose(target, bring_from)
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
    print("    %s scripts/paths.py --facts" % PY)
    return 0


if __name__ == "__main__":
    sys.exit(main())
