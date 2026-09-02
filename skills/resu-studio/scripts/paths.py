"""Where this person's own files live, and why that is not inside the skill.

A plugin is not updated in place. An update puts down a fresh copy of the plugin
folder and throws the old one away a couple of weeks later, so anything a person
built up inside it goes with it: their history, their facts ledger, every finished
CV. They would lose years of their own work to a routine update and nothing on
screen would connect the two events.

So the skill asks where its files go rather than assuming it is allowed to keep
them inside itself. Three answers, in order:

    1. CLAUDE_PLUGIN_DATA   the host's own folder for data that outlives an update.
                            Set when this is installed as a plugin. Always correct
                            when it is there, so nothing else is consulted.
    2. data-location.txt    one line, beside SKILL.md, holding a path. For someone
                            who wants their record on a synced drive, or anywhere
                            they choose. Absent unless they wrote it.
    3. <skill>/data         last resort, so a bare checkout still runs. Says so,
                            because it is the one answer an update can delete.

Nothing here deletes or moves anything. It resolves a folder and creates it.

    python3 scripts/paths.py            where everything goes, and why
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

_POINTER = os.path.join(SKILL, "data-location.txt")


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


def _pointer():
    """The path in `data-location.txt`, or None. Blank lines and `#` are ignored."""
    try:
        with io.open(_POINTER, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line and not line.startswith("#"):
                    return os.path.abspath(os.path.expanduser(line))
    except (IOError, OSError):
        pass
    return None


def resolve():
    """(folder, where_it_came_from, survives_an_update)."""
    env = os.environ.get("CLAUDE_PLUGIN_DATA")
    if env:
        env = os.path.abspath(os.path.expanduser(env))
        if _usable(env):
            return env, "CLAUDE_PLUGIN_DATA", True

    named = _pointer()
    if named:
        if _usable(named):
            return named, "data-location.txt", True
        sys.stderr.write(
            "data-location.txt names %s, which cannot be written to. Falling back.\n"
            % named)

    inside = os.path.join(SKILL, "data")
    return inside, "inside the skill", False


def data_dir():
    """The person's own folder. Created if it is not there yet."""
    path, _src, _safe = resolve()
    os.makedirs(path, exist_ok=True)
    return path


def documents_dir():
    """Where finished CVs and letters land."""
    path = os.path.join(data_dir(), DOCUMENTS)
    os.makedirs(path, exist_ok=True)
    return path


def sub(*parts):
    """A named folder inside the person's own folder, created."""
    path = os.path.join(data_dir(), *parts)
    os.makedirs(path, exist_ok=True)
    return path


def facts_file():
    """The reusable history. One per person, read by every advertisement."""
    return os.path.join(data_dir(), "facts.md")


def main():
    path, src, safe = resolve()
    print("The person's folder")
    print("  %s" % path)
    print("  chosen by: %s" % src)
    if safe:
        print("  a plugin update will not touch it.")
    else:
        print("  WARNING: this is inside the skill. A plugin update replaces the")
        print("  skill folder, so anything here goes with it. To move it, put one")
        print("  line — the folder you want — in:")
        print("    %s" % _POINTER)
    print()
    print("  documents : %s" % os.path.join(path, DOCUMENTS))
    print("  facts     : %s" % os.path.join(path, "facts.md"))
    print("  the CV as it arrived : %s" % os.path.join(path, "cv-source"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
