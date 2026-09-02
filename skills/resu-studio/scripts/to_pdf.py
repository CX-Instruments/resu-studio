"""HTML to PDF, through a real browser, with nothing re-drawn on the way.

The rule this file exists to keep: **the PDF is the skin, not a picture of it and
not a second opinion about it.** So it does not lay anything out. It hands the exact
file `render_cv.py` wrote to a real Chromium and asks Chromium to print it. Same
CSS, same webfonts, same palette variables, same paginate.js deciding where the
sheets break. What comes out is the page the studio previews, with the text still
text.

Why not one of the Python PDF libraries. WeasyPrint, ReportLab, fpdf and the rest
are their own layout engines. They would re-flow the CV against their own idea of
line breaking, their own font metrics and their own flexbox support, and the answer
would be close and wrong: a bar chart a millimetre short, a sidebar the wrong green,
a role that falls onto page two. Close and wrong is worse than absent, because
nobody checks a PDF they asked for.

Why not a screenshot. html2canvas and friends produce an image of the page. An image
has no text in it, so the applicant tracking system that reads the PDF finds nothing,
the recruiter cannot copy an email address out of it, and the file is ten times the
size. The whole document would be invisible to the first thing that reads it.

So: Chromium, headless, print-to-pdf. Vector text, embedded fonts, real colour.
"""

import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile


# Where a browser hides, in the order worth trying. Anything on PATH wins, because a
# person who installed one meant it. Then the usual install locations for each OS,
# then the Playwright cache, which is what a cloud sandbox tends to have.
_ON_PATH = ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable",
            "chrome", "microsoft-edge", "microsoft-edge-stable", "brave-browser")

_FIXED = (
    # macOS
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    # Linux
    "/usr/bin/chromium", "/usr/bin/chromium-browser", "/usr/bin/google-chrome",
    "/snap/bin/chromium",
    # Windows, including the same paths seen from WSL
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe",
    "/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
)

_GLOBS = (
    "/opt/pw-browsers/chromium-*/chrome-linux/chrome",
    "/opt/pw-browsers/chromium/chrome-linux/chrome",
    os.path.expanduser("~/.cache/ms-playwright/chromium-*/chrome-linux/chrome"),
    os.path.expanduser(
        "~/.cache/ms-playwright/chromium-*/chrome-mac/Chromium.app/Contents/MacOS/Chromium"),
    os.path.expanduser("~/Library/Caches/ms-playwright/chromium-*/chrome-mac/"
                       "Chromium.app/Contents/MacOS/Chromium"),
)


class NoBrowser(Exception):
    """No Chromium anywhere. Carries the sentence to show the person."""


def find_browser():
    """The browser to print with, or None. $CV_BROWSER overrides everything."""
    env = os.environ.get("CV_BROWSER") or os.environ.get("CHROME_PATH")
    if env and os.path.isfile(env):
        return env
    for name in _ON_PATH:
        got = shutil.which(name)
        if got:
            return got
    for path in _FIXED:
        if os.path.isfile(path):
            return path
    for pattern in _GLOBS:
        hits = sorted(glob.glob(pattern))
        if hits:
            return hits[-1]
    return None


ADVICE = (
    "No Chromium, Chrome or Edge was found here, and the PDF is printed by a real "
    "browser on purpose: it is the only way the file comes out as the skin actually "
    "draws it, with the palette, the meters and the typefaces intact.\n"
    "  This almost always means the script is running somewhere without a browser, "
    "usually the person's own machine. Run it in the session instead, which has "
    "one, and deliver the finished PDF to them.\n"
    "  If a browser is present under another name, set CV_BROWSER to it.\n"
    "  Do not ask the person to install a browser or to run anything themselves. The "
    "HTML this wrote already carries the print rules, so handing them that and "
    "letting them use their own browser's Save as PDF is the honest fallback."
)


def _page_count(path):
    """Pages in a finished PDF, so the caller can check it against the paginator."""
    try:
        with open(path, "rb") as f:
            blob = f.read()
    except OSError:
        return 0
    n = len(re.findall(br"/Type\s*/Page[^s]", blob))
    return n or len(re.findall(br"/Type\s*/Page\b", blob))


def html_to_pdf(html_path, pdf_path, browser=None, timeout=180, wait_ms=12000):
    """Print one HTML file to one PDF. Returns the page count.

    `wait_ms` is virtual time, not wall clock. Chromium stops the clock while a
    request is in flight, so this is a budget for the webfonts to arrive and for
    paginate.js to finish measuring, not a sleep. It costs nothing when they are fast.
    """
    exe = browser or find_browser()
    if not exe:
        raise NoBrowser(ADVICE)

    html_path = os.path.abspath(html_path)
    pdf_path = os.path.abspath(pdf_path)
    profile = tempfile.mkdtemp(prefix="cvpdf-")
    url = "file://" + html_path.replace(os.sep, "/")
    if not url.startswith("file:///"):
        url = "file:///" + html_path.replace(os.sep, "/").lstrip("/")

    argv = [
        exe,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-extensions",
        "--user-data-dir=" + profile,
        # The CV is drawn at 96dpi CSS pixels. Give the print the same window so
        # nothing measures against a different viewport than the studio did.
        "--window-size=794,1123",
        # No "page 1/2" and no file path stamped across the header. A CV with the
        # browser's furniture on it is not a CV anybody sends.
        "--no-pdf-header-footer",
        "--print-to-pdf-no-header",
        # Let the fonts land and the paginator settle before the paper is drawn.
        "--virtual-time-budget=%d" % int(wait_ms),
        "--run-all-compositor-stages-before-draw",
        "--print-to-pdf=" + pdf_path,
        url,
    ]

    # Rendering the same skin twice replaces the file rather than leaving two, so a
    # person ends up with the version they last asked for and not a folder of near
    # duplicates. The old one is removed first so a browser that fails halfway cannot
    # leave a truncated file wearing the name of a good one.
    #
    # The exception worth naming: on Windows a PDF open in a viewer is locked, and
    # deleting it raises. Swallowing that produces a baffling failure two steps later
    # ("the browser wrote no usable PDF"), when the real answer is one sentence long.
    if os.path.exists(pdf_path):
        try:
            os.remove(pdf_path)
        except PermissionError:
            raise RuntimeError(
                "%s is open in another program, so it cannot be replaced.\n"
                "  Close it and run this again." % os.path.basename(pdf_path))
        except OSError as exc:
            raise RuntimeError("could not replace %s: %s"
                               % (os.path.basename(pdf_path), exc))

    try:
        proc = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              timeout=timeout)
    except subprocess.TimeoutExpired:
        shutil.rmtree(profile, ignore_errors=True)
        raise RuntimeError("the browser did not finish printing within %ds" % timeout)
    finally:
        shutil.rmtree(profile, ignore_errors=True)

    if not os.path.isfile(pdf_path) or os.path.getsize(pdf_path) < 1000:
        err = (proc.stderr or b"").decode("utf-8", "replace").strip()
        tail = "\n  ".join(err.splitlines()[-6:]) if err else "(the browser said nothing)"
        raise RuntimeError("the browser ran but wrote no usable PDF.\n  %s" % tail)

    with open(pdf_path, "rb") as f:
        if f.read(5) != b"%PDF-":
            raise RuntimeError("what the browser wrote is not a PDF")

    return _page_count(pdf_path)


def has_real_fonts(pdf_path):
    """True when the PDF carries embedded font programs rather than substitutes.

    A missing webfont is the one failure that looks fine and is not: the layout
    survives, the letters are somebody else's. Worth reporting, never worth silently
    accepting.
    """
    try:
        with open(pdf_path, "rb") as f:
            blob = f.read()
    except OSError:
        return False
    return b"/FontFile" in blob


def font_names(pdf_path):
    """The faces actually embedded, so the caller can print them and be believed."""
    try:
        with open(pdf_path, "rb") as f:
            blob = f.read()
    except OSError:
        return []
    # A PDF names a face in more than one place, and which one it uses depends on
    # how the font was subset. A variable font comes through as a descriptor with a
    # /FontName and no /BaseFont at all, so reading only /BaseFont reports a face
    # that is present as missing, which would make the guard below refuse good work.
    found = re.findall(br"/(?:BaseFont|FontName)\s*/(?:[A-Z]{6}\+)?([A-Za-z0-9\-]+)",
                       blob)
    found += re.findall(br"/FontFamily\s*\(([^)]{1,64})\)", blob)
    out = []
    for name in found:
        label = name.decode("latin-1").strip()
        if label and label not in out:
            out.append(label)
    return out


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.stderr.write("usage: to_pdf.py <in.html> <out.pdf>\n")
        sys.exit(2)
    try:
        pages = html_to_pdf(sys.argv[1], sys.argv[2])
    except NoBrowser as exc:
        sys.stderr.write(str(exc) + "\n")
        sys.exit(3)
    except RuntimeError as exc:
        sys.stderr.write(str(exc) + "\n")
        sys.exit(1)
    print("wrote %s, %d page%s" % (sys.argv[2], pages, "" if pages == 1 else "s"))
