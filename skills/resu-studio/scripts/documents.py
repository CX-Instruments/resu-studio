"""What this person has produced, so that nothing is replaced without them knowing.

Two applications can produce documents with identical names. The filename carries
the person's name, the role and the date, and the role is only there when it was
given, so two advertisements answered on one afternoon, with no role passed, write
`<Name> - 20260901 - CV.pdf` twice, and the second one silently takes the place
of the first. Nothing on screen says so. The person finds out when they open what
they thought was Tuesday's application.

Two applications for the same role at different employers do it too, and that is the
commoner case: the same advertised job title at two employers, both assembled from
`cv-tailored.md`, both printed the same afternoon. The role matches, the source
matches, and without the employer the record cannot tell them apart. So the employer
is part of what a document is, and a record with no employer is never treated as the
same application as one that has an employer.

Re-rendering the same document should overwrite: somebody trying six skins does not
want six files. Answering a different advertisement should not. The filename cannot
tell those apart, so a small record is kept beside the documents saying which
advertisement each file was for. When the answer differs, the old file is kept under
a dated name instead of being written over.

The record is keyed on where the file is, not on what it is called. Documents can be
written outside the documents folder with `--pdf-dir`, and two folders holding a
`CV.pdf` are two documents, not one; keying on the bare name made the second one
overwrite the first one's provenance and left everything outside the documents folder
permanently reported as missing.

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

_MIGRATED = False       # an old ledger is rewritten once per run, never discarded


def _ledger_path():
    return paths.documents_ledger()


def key_for(path):
    """How a file is named in the ledger: its path relative to the data folder.

    Relative, so the whole record survives the folder being moved or synced to
    another machine. Absolute for anything outside it, which is where `--pdf-dir`
    puts things. Separators are written as `/` either way so that a ledger made on
    Windows and read on Linux is the same ledger.
    """
    ap = os.path.abspath(os.path.expanduser(path))
    try:
        base = os.path.abspath(paths.data_dir())
        rel = os.path.relpath(ap, base)
        if rel != os.pardir and not rel.startswith(os.pardir + os.sep):
            return rel.replace(os.sep, "/")
    except (OSError, ValueError):
        pass
    return ap.replace(os.sep, "/")


def _migrate(data):
    """An old ledger keyed on bare filenames, brought forward. Nothing is dropped.

    A file that is still where the old ledger assumed, in the documents folder, is
    re-keyed to its path and gains that path. One that is not is kept exactly as it
    was, under its old name, so a history of documents somebody has since filed away
    is still their history.
    """
    if not isinstance(data, dict):
        return {}, False
    out, changed = {}, False
    try:
        docs = paths.documents_dir()
    except OSError:
        docs = None
    for name, rec in data.items():
        if not isinstance(rec, dict):
            continue
        if "path" in rec and rec.get("path"):
            out[name] = rec
            continue
        rec = dict(rec)
        rec.setdefault("name", os.path.basename(name))
        rec.setdefault("employer", "")
        guess = os.path.join(docs, rec["name"]) if docs else None
        if guess and os.path.exists(guess):
            rec["path"] = guess
            out[key_for(guess)] = rec
        else:
            rec["path"] = ""
            out[name] = rec
        changed = True
    return out, changed


def load_ledger(path):
    """The ledger stored at one exact file, in the shape this version keys on.

    Named and public because it is not always this person's current ledger that is
    being read: `paths.py` reads an older one out of the plugin folder to bring it
    forward, and how a record is shaped and keyed is this file's business, not its.
    """
    try:
        with io.open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (IOError, OSError, ValueError):
        return {}
    if not isinstance(data, dict):
        return {}
    data, _changed = _migrate(data)
    return data


def save_ledger(data, path):
    """Write a ledger to one exact file. Silent on failure, deliberately."""
    try:
        with io.open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(json.dumps(data, indent=2, ensure_ascii=False))
    except (IOError, OSError):
        pass          # a record that cannot be written must never stop a render


def _load():
    global _MIGRATED
    try:
        with io.open(_ledger_path(), encoding="utf-8") as fh:
            data = json.load(fh)
            if not isinstance(data, dict):
                return {}
    except (IOError, OSError, ValueError):
        return {}
    data, changed = _migrate(data)
    if changed and not _MIGRATED:
        _MIGRATED = True
        _save(data)
    return data


def _save(data):
    save_ledger(data, _ledger_path())


def _find(data, path):
    """(key, record) for this file, matching case the way the filesystem does.

    A folder mounted from Windows hands back `CV.pdf` and `cv.pdf` as the same
    file, so a lookup that respects case would file one document as two and
    overwrite the first without a word.
    """
    want = key_for(path)
    if want in data:
        return want, data[want]
    low = want.lower()
    for k, rec in data.items():
        if k.lower() == low:
            return k, rec
    # An old entry that migration could not place, still under its bare filename.
    base = os.path.basename(path).lower()
    for k, rec in data.items():
        if k.lower() == base and not rec.get("path"):
            return k, rec
    return want, None


def role_of(path):
    """Which advertisement this file was produced for, or "" if unrecorded."""
    _k, rec = _find(_load(), path)
    return (rec or {}).get("role", "")


def employer_of(path):
    """Which employer this file was produced for, or "" if unrecorded."""
    _k, rec = _find(_load(), path)
    return (rec or {}).get("employer", "")


def record(path, role, kind, source="", employer="", job=""):
    """Record what a file is, so a later render can tell same-job from new-job.

    `job` is the id of the job folder this document was made for, when there is one.
    Resu Desk reads it to list each job's documents under that job.
    """
    data = _load()
    key, old = _find(data, path)
    if old is not None and key in data:
        del data[key]
    data[key_for(path)] = {
        "role": role or "",
        "employer": employer or "",
        "source": os.path.basename(source or ""),
        "kind": kind,
        "name": os.path.basename(path),
        "path": os.path.abspath(os.path.expanduser(path)),
        "written": time.strftime("%Y-%m-%d %H:%M"),
    }
    if job:
        data[key_for(path)]["job"] = job
    _save(data)


def note(path, role, kind, source="", employer="", job=""):
    """The older name for `record`. Kept so existing callers keep working."""
    record(path, role, kind, source=source, employer=employer, job=job)


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
            key, was = _find(data, path)
            if was:
                was = dict(was)
                was["name"] = os.path.basename(kept)
                was["path"] = os.path.abspath(kept)
                data[key_for(kept)] = was
                data.pop(key, None)
                _save(data)
            return kept
    return None


def _same_employer(was, employer):
    """Two employers agree, or neither was named. One named and one not is not agreement.

    A record made before employers were kept says nothing about which employer it
    was for, and guessing that it was this one is exactly the guess that overwrites
    somebody's other application.
    """
    a = (was or "").strip().lower()
    b = (employer or "").strip().lower()
    if bool(a) != bool(b):
        return False
    return a == b


def protect(path, role, source="", employer=""):
    """Keep the file at `path` unless this is a re-render of the same document.

    An application is identified by the advertisement it answers: the employer, the
    role, and the markdown it was built from. All three the same is somebody trying
    another skin, and overwriting is exactly what they want. Anything else is a
    different application that happens to produce the same filename, and the earlier
    file is kept.

    Erring towards keeping is deliberate. A spare file is a tidying job; a document
    written over is a piece of work nobody can get back.
    """
    if not os.path.exists(path):
        return None
    _key, was = _find(_load(), path)
    if was is None:
        # Written before any record existed. Its provenance is unknown, so it is
        # kept rather than assumed to be a draft of this same application.
        return keep_aside(path)
    same = ((was.get("role", "") or "").strip().lower()
            == (role or "").strip().lower()
            and _same_employer(was.get("employer", ""), employer)
            and (was.get("source", "") or "") == os.path.basename(source or ""))
    return None if same else keep_aside(path)


def _heading(rec):
    """How one application is named on screen: the role, and the employer if known."""
    role = (rec.get("role") or "").strip()
    emp = (rec.get("employer") or "").strip()
    job = (rec.get("job") or "").strip()
    if job:
        return "%s%s   [job %s]" % (role or "(role not recorded)",
                                   (" at " + emp) if emp else "", job)
    if role and emp:
        return "%s at %s" % (role, emp)
    if role:
        return role
    if emp:
        return "(role not recorded) at %s" % emp
    return "(role not recorded)"


def roles():
    """Every advertisement this person has produced documents for, newest first."""
    seen = {}
    for key, rec in _load().items():
        head = _heading(rec)
        when = rec.get("written", "")
        entry = seen.setdefault(head, {"when": when, "files": []})
        if when > entry["when"]:
            entry["when"] = when
        entry["files"].append((rec.get("name") or os.path.basename(key),
                               rec.get("path") or ""))
    return sorted(seen.items(), key=lambda kv: kv[1]["when"], reverse=True)


def printed_for(role, employer=""):
    """Has a PDF ever been produced for this advertisement?"""
    for key, rec in _load().items():
        if (rec.get("role") or "").strip().lower() != (role or "").strip().lower():
            continue
        if employer and not _same_employer(rec.get("employer", ""), employer):
            continue
        name = (rec.get("name") or key).lower()
        if name.endswith(".pdf"):
            return True
    return False


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] in ("-h", "--help"):
            sys.stdout.write("usage: documents.py\n"
                             "  what is in the documents folder, and what each "
                             "document was for. Takes no arguments.\n")
            return 0
        sys.stderr.write("usage: documents.py   (it takes no arguments)\n")
        return 2

    folder = paths.documents_dir()
    rs = roles()
    print("Documents folder")
    print("  %s" % folder)
    print()
    if not rs:
        print("  Nothing produced yet.")
        return 0
    for head, info in rs:
        print("  %s" % head)
        print("    last written %s" % info["when"])
        for name, where in sorted(set(info["files"])):
            # Where the file was actually written, which is not always this folder:
            # --pdf-dir puts documents wherever it was told to.
            full = where or os.path.join(folder, name)
            gone = "" if os.path.exists(full) else "   (moved or deleted)"
            elsewhere = ""
            if where and os.path.dirname(os.path.abspath(where)) != os.path.abspath(folder):
                elsewhere = "   in %s" % os.path.dirname(where)
            print("      %s%s%s" % (name, elsewhere, gone))
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
