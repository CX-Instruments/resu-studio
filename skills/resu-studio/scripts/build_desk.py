"""Build Resu Desk: every application this person has, in one page.

    python3 scripts/build_desk.py            writes 4 Finished documents/Resu Desk.html
    python3 scripts/build_desk.py --out F    somewhere else

The Desk is a picture of the records. It reads each job's `job.json` and the documents
ledger, and draws one row per job: the employer and role, the stage, the closing date,
the score before and after tailoring, and a link to every Studio and PDF made for it.
Nothing in it is typed by hand, so it cannot disagree with the records it was built
from, and it is rebuilt whenever one of them changes: by `jobs.py` after any command
that writes a record, by `build_studio.py` after it writes a studio, and by
`render_cv.py` after it prints.

A person can change a stage, a closing date or add a note on the page. The page cannot
write those back, because it is a file, so they travel the way the Studio's decisions
do: through "hand to AI" or the saved `desk-updates.json`, into
`jobs.py apply-desk`, which writes them and rebuilds this page.

Standard library only.

    0   written
    2   the command line was wrong
    5   the page could not be written
"""

import argparse
import base64
import datetime
import hashlib
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TEMPLATE = os.path.join(ROOT, "assets", "desk.html")
LABEL_FONT = os.path.join(ROOT, "assets", "fonts", "archivo-narrow-v35-latin-700.woff2")

sys.path.insert(0, HERE)
import paths      # noqa: E402
import documents  # noqa: E402
import jobs       # noqa: E402

DESK_NAME = "Resu Desk.html"

#: The kinds of document a row links to, in the order they are listed.
KINDS = ("studio", "cv", "letter")

#: The placeholder in the template. Replaced whole, once.
PLACEHOLDER_RE = re.compile(r"^const DESK = \{.*?\};$", re.M)


def desk_path():
    return os.path.join(paths.documents_dir(), DESK_NAME)


def folder_key():
    """A short name for this person's folder, for the page's browser storage.

    Pages opened from disk share one storage area in most browsers. Keyed on the folder,
    a test Desk and a real one on the same machine cannot see each other's unsent
    changes. Hashed, so the folder's path is not written into the page.
    """
    return hashlib.sha1(os.path.abspath(paths.data_dir()).encode("utf-8")).hexdigest()[:10]


def _href(target, base):
    """A link from the Desk's folder to a file, relative when it can be, with each part
    escaped so a space or a # in a filename does not break it."""
    from urllib.parse import quote
    try:
        rel = os.path.relpath(target, base)
        return "/".join(quote(p) for p in rel.replace(os.sep, "/").split("/"))
    except ValueError:
        # A different drive on Windows has no relative path. An absolute file link
        # still opens from the same machine.
        return "file:///" + quote(os.path.abspath(target).replace(os.sep, "/").lstrip("/"))


def _where(target):
    """Where a file is, written for a person: inside their folder, relative to it."""
    try:
        rel = os.path.relpath(target, paths.data_dir())
        if not rel.startswith(os.pardir):
            return rel.replace(os.sep, "/")
    except ValueError:
        pass
    return os.path.abspath(target)


def _norm(text):
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def job_documents(rec, ledger, base):
    """Every document on record for this job, Studio first, newest first within a kind.

    A record carrying this job's id belongs to it. So does an older record with no job
    at all whose role and employer match exactly, because documents made before jobs
    existed are still this application's documents. A record carrying a different job's
    id never does, even with the same role and employer: that is the second application
    somebody made with `--again`.
    """
    out = []
    for key, d in ledger.items():
        if not isinstance(d, dict) or d.get("kind") not in KINDS:
            continue
        if d.get("job"):
            if d["job"] != rec["id"]:
                continue
        elif not (_norm(d.get("role")) == _norm(rec.get("role"))
                  and _norm(d.get("employer")) == _norm(rec.get("employer"))):
            continue
        path = d.get("path") or os.path.join(paths.data_dir(), key)
        out.append({
            "kind": d["kind"],
            "name": d.get("name") or os.path.basename(path),
            "href": _href(path, base),
            "where": _where(path),
            "written": d.get("written", ""),
            "exists": os.path.isfile(path),
        })
    out.sort(key=lambda x: x["written"], reverse=True)
    out.sort(key=lambda x: KINDS.index(x["kind"]))
    return out


def desk_data(base):
    ledger = documents.load_ledger(paths.documents_ledger())
    rows = []
    for rec in jobs.all_jobs():
        scores = rec.get("scores") or {}
        rows.append({
            "id": rec["id"],
            "role": rec.get("role", ""),
            "employer": rec.get("employer", ""),
            "stage": rec.get("stage", "Saved"),
            "closes": rec.get("closes", ""),
            "link": rec.get("link", "") if re.match(r"^https?://", rec.get("link", "")) else "",
            "updated": rec.get("updated", ""),
            "before": scores.get("before"),
            "after": scores.get("after"),
            "notes": rec.get("notes") or [],
            "docs": job_documents(rec, ledger, base),
        })
    return {
        "schema": 1,
        "built": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "key": folder_key(),
        "stages": list(jobs.STAGES),
        "closed": list(jobs.CLOSED),
        "jobs": rows,
    }


def _script_json(value):
    """JSON that is safe inside a <script> element.

    A note that says `</script>` would otherwise end the script in the middle of the data,
    and the two line separators JavaScript treats as line breaks would end the string.
    """
    text = json.dumps(value, ensure_ascii=False)
    return (text.replace("</", "<\\/").replace("\u2028", "\\u2028")
            .replace("\u2029", "\\u2029"))


def build(out=None):
    """Write the Desk. Returns the path. Raises OSError or ValueError when it cannot."""
    out = out or desk_path()
    base = os.path.dirname(os.path.abspath(out))
    with io.open(TEMPLATE, encoding="utf-8") as fh:
        page = fh.read()
    if not PLACEHOLDER_RE.search(page):
        raise ValueError("assets/desk.html has no `const DESK = {...};` line to fill, so "
                         "the Desk would open empty.")
    data = desk_data(base)
    page = PLACEHOLDER_RE.sub(lambda m: "const DESK = %s;" % _script_json(data), page, count=1)
    if os.path.isfile(LABEL_FONT):
        with io.open(LABEL_FONT, "rb") as fh:
            face = base64.b64encode(fh.read()).decode("ascii")
        page = page.replace(
            '<style id="deskfaces"></style>',
            '<style id="deskfaces">@font-face{font-family:"Archivo Narrow";font-weight:700;'
            'src:url(data:font/woff2;base64,%s) format("woff2")}</style>' % face, 1)
    # Written beside and swapped in, so a Desk someone has open is never half a page.
    # A failed swap takes its temporary file with it rather than leaving litter in the
    # folder a person opens to find their documents.
    tmp = out + ".tmp"
    try:
        with io.open(tmp, "w", encoding="utf-8", newline="") as fh:
            fh.write(page)
        os.replace(tmp, out)
    except OSError:
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise
    return out


def refresh(quiet=True):
    """Rebuild the Desk after something changed. Never raises.

    Called at the end of commands whose own job is something else, so a Desk that
    cannot be written must not turn a studio that was written into a failure. It says
    so in one line and the command carries on.
    """
    try:
        path = build()
        if not quiet:
            print("  desk   : %s" % path)
        return path
    except Exception as e:                                     # noqa: BLE001
        sys.stderr.write("resu-studio: Resu Desk was not updated (%s). Everything else "
                         "worked. Run %s scripts/build_desk.py to try again.\n"
                         % (e, paths.PY))
        return None


def main(argv=None):
    ap = argparse.ArgumentParser(prog="build_desk.py",
                                 description="Build Resu Desk from every job's record.")
    ap.add_argument("--out", default=None, help="where to write. Default: the documents folder")
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    try:
        path = build(a.out)
    except (OSError, ValueError) as e:
        sys.stderr.write("build_desk.py: the Desk could not be written: %s\n" % e)
        return 5
    n = len(paths.known_jobs())
    print("wrote %s" % path)
    print("  %d job%s on it" % (n, "" if n == 1 else "s"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
