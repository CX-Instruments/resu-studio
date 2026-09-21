"""Open one built Studio once. Rebuilds do not reset the launch guard.

No shell, file associations, retries, or browser-profile creation. A dispatched
process is not proof that the user saw the page; always deliver the file links.
"""
import argparse
from pathlib import Path
import subprocess
import sys

import to_pdf


def open_studio(filename, again=False):
    page = Path(filename).resolve(strict=True)
    if page.suffix.lower() != ".html":
        raise ValueError("Choose the generated Studio HTML file.")
    content = page.read_text(encoding="utf-8")
    if "const CV =" not in content or "BUILD_STAMP" in content:
        raise ValueError("This is not a built Studio. Use the exact path printed by build_studio.py.")
    marker = page.with_name("." + page.name + ".open-attempt")
    if marker.exists() and not again:
        return "Already attempted for this Studio. Refresh the existing tab or use its link; no new browser was launched."
    browser = to_pdf.find_browser()
    if not browser:
        return "No browser found. Open the delivered Studio link in your browser; no launch was attempted."
    # Reserve before dispatch, including on failure. Concurrent/repeated calls must
    # not create a launch loop. Only an explicit user request warrants --again.
    try:
        with marker.open("w" if again else "x", encoding="utf-8") as f:
            f.write(page.as_uri() + "\n")
    except FileExistsError:
        return "Already attempted for this Studio; no new browser was launched."
    subprocess.Popen([browser, page.as_uri()], stdin=subprocess.DEVNULL,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return "One browser launch requested for " + str(page) + ". Refresh this tab after rebuilds."


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("studio", help="Exact generated Studio path printed by the build")
    parser.add_argument("--again", action="store_true", help="Only when the user explicitly asks to reopen")
    args = parser.parse_args(argv)
    try:
        print(open_studio(args.studio, args.again))
        return 0
    except (OSError, ValueError) as exc:
        print("Studio was not opened: %s. Deliver the file links; do not retry automatically." % exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
