"""What this person has produced, so that nothing is replaced without them knowing.

Two applications can produce documents with identical names. The filename carries
the person's name, the role and the date, and the role is only there when it was
given — so two advertisements answered on one afternoon, with no role passed, write
`Alex Taylor - 20260901 - CV.pdf` twice, and the second one silently takes the place
of the first. Nothing on screen says so. The person finds out when they open what
they thought was Tuesday's application.

Re-rendering the same document should overwrite: somebody trying six skins does not
want six files. Answering a different advertisement should not. The filename cannot
tell those apart, so a small record is kept beside the documents saying which
advertisement each file was for. When the answer differs, the old file is kept under
a dated name instead of being written over.

    python3 scripts/documents.py           what is in the folder, and for what
"""

import io
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import paths  # noqa: E402

LEDGER = "documents.json"


def _ledger_path():
    return os.path.join(paths.data_dir(), LEDGER)


def _load():
    try:
        with io.open(_ledger_path(), encoding="utf-8") as fh:
            data = json.load(fh)
            return data if isinstance(data, dict) else {}
    except (IOError, OSError, ValueError):
        return {}


def _save(data):
    try:
        with io.open(_ledger_path(), "w", encoding="utf-8", newline="") as fh:
            fh.write(json.dumps(data, indent=2, ensure_ascii=False))
    except (IOError, OSError):
        pass          # a record that cannot be written must never stop a render


def role_of(path):
    """Which advertisement this file was produced for, or "" if unrecorded."""
    return _load().get(os.path.basename(path), {}).get("role", "")


def note(path, role, kind, source=""):
    """Record what a file is, so a later render can tell same-job from new-job."""
    data = _load()
    data[os.path.basename(path)] = {
        "role": role or "",
        "source": os.path.basename(source or ""),
        "kind": kind,
        "written": time.strftime("%Y-%m-%d %H:%M"),
    }
    _save(data)


def keep_aside(path):
    """Move an existing file out of the way under a dated name. Returns where.

    Called only when the file about to be written belongs to a different
    advertisement, so that a person answering a second job never loses the first.
    """
    if not os.path.exists(path):
        return None
    stem, ext = os.path.splitext(path)
    for n in range(1, 40):
        tag = time.strftime("%Y-%m-%d") + ("" if n == 1 else " (%d)" % n)
        kept = "%s (replaced %s)%s" % (stem, tag, ext)
        if not os.path.exists(kept):
            try:
                os.rename(path, kept)
            except OSError:
                return None
            data = _load()
            was = data.get(os.path.basename(path))
            if was:
                data[os.path.basename(kept)] = was
                _save(data)
            return kept
    return None


def protect(path, role, source=""):
    """Keep the file at `path` unless this is a re-render of the same document.

    An application is identified by the advertisement it answers and the markdown it
    was built from. Same role and same source is somebody trying another skin, and
    overwriting is exactly what they want. Anything else is a different application
    that happens to produce the same filename, and the earlier file is kept.

    Erring towards keeping is deliberate. A spare file is a tidying job; a document
    written over is a piece of work nobody can get back.
    """
    if not os.path.exists(path):
        return None
    was = _load().get(os.path.basename(path))
    if was is None:
        # Written before any record existed. Its provenance is unknown, so it is
        # kept rather than assumed to be a draft of this same application.
        return keep_aside(path)
    same = ((was.get("role", "") or "").strip().lower()
            == (role or "").strip().lower()
            and (was.get("source", "") or "") == os.path.basename(source or ""))
    return None if same else keep_aside(path)


def roles():
    """Every advertisement this person has produced documents for, newest first."""
    seen = {}
    for name, rec in _load().items():
        r = rec.get("role") or "(role not recorded)"
        when = rec.get("written", "")
        if r not in seen or when > seen[r]["when"]:
            seen[r] = {"when": when, "files": []}
    for name, rec in _load().items():
        r = rec.get("role") or "(role not recorded)"
        seen[r]["files"].append(name)
    return sorted(seen.items(), key=lambda kv: kv[1]["when"], reverse=True)


def printed_for(role):
    """Has a PDF ever been produced for this advertisement?"""
    for name, rec in _load().items():
        if (rec.get("role") or "").strip().lower() == (role or "").strip().lower():
            if name.lower().endswith(".pdf"):
                return True
    return False


def main():
    folder = paths.documents_dir()
    rs = roles()
    print("Documents folder")
    print("  %s" % folder)
    print()
    if not rs:
        print("  Nothing produced yet.")
        return 0
    for role, info in rs:
        print("  %s" % role)
        print("    last written %s" % info["when"])
        for f in sorted(info["files"]):
            here = "" if os.path.exists(os.path.join(folder, f)) else "   (moved or deleted)"
            print("      %s%s" % (f, here))
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
