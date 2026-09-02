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
    2. CLAUDE_PLUGIN_DATA   the host's own folder for data that outlives an update.
                            Set when this is installed as a plugin. Used when no
                            pointer was written.
    3. ~/.resu-studio       last resort, and still outside the plugin, so a bare
                            checkout keeps this person's work through an update.
    4. <skill>/data         only when a home folder cannot be made at all. Says so
                            loudly, because it is the one answer an update deletes.

A pointer is checked before it is believed. A Windows path such as `D:\\CVs`, or
anything holding a backslash, is not a path this session can see: it would be
created as one directory with backslashes in its name, in some working directory,
and every finished document would go there and never be found. It is refused, by
name, with what to write instead.

Nothing here deletes or moves anything. It resolves a folder and creates it.

    python3 scripts/paths.py            where everything goes, and why
    python3 scripts/paths.py --facts    just the path, for a command line
"""

import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)

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

#: The last resort of all, inside the skill. An update replaces this folder.
INSIDE = os.path.join(SKILL, "data")

_WARNED = False
_RESOLVED = None      # resolve() is asked many times per run and cannot change
                      # inside one; caching it also keeps a complaint about a bad
                      # pointer to one line instead of one per call.


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

    if re.match(r"^[A-Za-z]:[\\/]", raw) or "\\" in raw:
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
                      "from, so it is refused. Write the whole path, starting at /."
                      % (label, raw))

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
        return _RESOLVED
    _RESOLVED = _resolve_once()
    return _RESOLVED


def _resolve_once():
    env = os.environ.get("CLAUDE_PLUGIN_DATA")

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
        return path, label, True

    if env:
        # The host made this folder up, and may not have created it yet, so its
        # parent is not required to exist. The rest of the checks still apply: a
        # backslash in here would build the same junk folder as anywhere else.
        path, complaint = check_pointer_text(env, "CLAUDE_PLUGIN_DATA",
                                             require_parent=False)
        if complaint:
            sys.stderr.write("resu-studio: %s\n" % complaint)
        elif _usable(path):
            return path, "CLAUDE_PLUGIN_DATA", True

    if _usable(HOME_DIR):
        return HOME_DIR, "~/.resu-studio (nothing else was named)", True

    return INSIDE, "inside the skill (nowhere else could be created)", False


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
        "update deletes it. Run python3 scripts/paths.py to move them.\n" % path)


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
    """The CV as it arrived, kept exactly as it was handed over."""
    return os.path.join(data_dir(), "cv-source")


#: What each one-path flag prints. Nothing else is printed with these, so they can
#: be used as `--facts "$(python3 scripts/paths.py --facts)"`.
_ONE_PATH = {
    "--data": lambda: data_dir(),
    "--facts": lambda: facts_file(),
    "--answers": lambda: answers_file(),
    "--documents": lambda: documents_dir(),
    "--cv-source": lambda: cv_source_dir(),
}


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)

    for arg in argv:
        if arg in _ONE_PATH:
            sys.stdout.write(_ONE_PATH[arg]() + "\n")
            return 0
        if arg in ("-h", "--help"):
            sys.stdout.write(
                "usage: paths.py [--data|--facts|--answers|--documents|--cv-source]\n"
                "  no arguments : where everything goes, and why\n"
                "  a flag       : that one path, on its own line, and nothing else\n")
            return 0
        if arg.startswith("-"):
            sys.stderr.write("paths.py: unknown option %s. Known: %s\n"
                             % (arg, " ".join(sorted(_ONE_PATH))))
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
    env = os.environ.get("CLAUDE_PLUGIN_DATA")
    if env and src != "CLAUDE_PLUGIN_DATA":
        print("  CLAUDE_PLUGIN_DATA is set to %s and was not used: a pointer file "
              "is a person's own choice and comes first." % env)

    print()
    print("  documents : %s" % os.path.join(path, DOCUMENTS))
    print("  facts     : %s" % os.path.join(path, "facts.md"))
    print("  answers   : %s" % os.path.join(path, "answers.md"))
    print("  the CV as it arrived : %s" % os.path.join(path, "cv-source"))
    print()
    print("  For a command line, one path and nothing else:")
    print("    python3 scripts/paths.py --facts")
    print("    %s" % " ".join(sorted(_ONE_PATH)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
