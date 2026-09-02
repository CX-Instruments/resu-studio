"""Put the typefaces inside the skill, once, so nothing has to fetch them again.

Run this on a machine with internet. With no arguments it takes **every** webfont
family in `assets/fonts.json`, because the studio lets a person pick any of them and
a face that only works sometimes is a face that does not work.

    python3 scripts/fetch_fonts.py            # all of them. The normal thing to run
    python3 scripts/fetch_fonts.py --check    # what is covered. No network needed
    python3 scripts/fetch_fonts.py lora       # one family, if you know why

After it runs, every render carries its own faces: the studio preview, the HTML and
the PDF all draw the same letters on a machine with no network at all.

Why this exists. The renderer used to link the faces from Google's font server. That
works in a browser on a normal connection and fails in exactly the place PDFs get
made: a sandbox, a locked-down network, a laptop offline on a train. It does not fail
loudly either. The browser substitutes a face with different metrics, re-flows every
line against it, and writes a document that looks finished. Carrying the files
removes the question.

Adding a face to the studio is adding a row to `assets/fonts.json` and running this
again. Nothing here is a fixed list.
"""

import json
import os
import re
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(os.path.dirname(HERE), "assets")
OUT = os.path.join(ASSETS, "fonts")

# The CSS the font server returns depends on who is asking. An old user agent is sent
# ttf, a current one woff2, which is a third of the size for the same letters.
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

# Basic Latin. A CV is written in it, and it is the block that decides whether a
# subset is the one worth keeping.
LATIN = "U+0000-00FF"


def _get(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as r:
        data = r.read()
    return data if binary else data.decode("utf-8")


def families():
    with open(os.path.join(ASSETS, "fonts.json"), encoding="utf-8") as f:
        return json.load(f).get("fonts", {})


def parse_css(css):
    """Every @font-face in the stylesheet, as {weight, url, latin}.

    `weight` is the declaration verbatim: "400", or "100 900" when the family ships
    one variable file covering the range.
    """
    out = []
    for raw in css.split("@font-face")[1:]:
        block = raw.split("}")[0]
        weight = re.search(r"font-weight:\s*([0-9]+(?:\s+[0-9]+)?)", block)
        url = re.search(r"url\((https://[^)]+\.(?:woff2|woff|ttf))\)", block)
        if not weight or not url:
            continue
        rng = re.search(r"unicode-range:\s*([^;]+)", block)
        out.append({"weight": " ".join(weight.group(1).split()),
                    "url": url.group(1),
                    "latin": (LATIN in rng.group(1)) if rng else True,
                    "ranged": bool(rng)})
    return out


def pick(faces):
    """Which files to keep, as (suffix, url).

    Two traps live here.

    One: a family is served as several subsets per weight — cyrillic, greek,
    vietnamese, latin-ext, latin — and latin is usually **last**. Taking the first
    block that matches a weight gets Cyrillic, which has no Latin glyphs in it at
    all, so the browser silently falls back for every letter on the page and the
    embedding was worthless. So the subset is chosen by its unicode-range, never by
    its position.

    Two: several families now ship as one variable file declaring `font-weight: 100
    900`. Asking such a file for 400 and 700 as two fixed rules gets one real weight
    and one the browser fakes by smearing it. A range is kept as a single variable
    file and declared as a range.
    """
    latin = [f for f in faces if f["latin"]] or faces
    by_weight = {}
    for f in latin:
        by_weight.setdefault(f["weight"], f["url"])

    variable = [w for w in by_weight if " " in w]
    if variable:
        # One file covers every weight the page can ask for.
        return [("variable", by_weight[variable[0]])]

    out = []
    for want in ("400", "700"):
        if want in by_weight:
            out.append((want, by_weight[want]))
    return out


def covered(key):
    """What is already on disk for one family: 'variable', '400+700', or None."""
    for ext in ("woff2", "woff", "ttf", "otf"):
        if os.path.isfile(os.path.join(OUT, "%s-variable.%s" % (key, ext))):
            return "variable"
    got = []
    for weight in (400, 700):
        for ext in ("woff2", "woff", "ttf", "otf"):
            if os.path.isfile(os.path.join(OUT, "%s-%d.%s" % (key, weight, ext))):
                got.append(weight)
                break
    return "400+700" if len(got) == 2 else None


def fetch(key, entry):
    """One family. Returns (files written, note)."""
    fam = entry.get("g")
    if not fam:
        return 0, "the machine's own face, nothing to fetch"
    css = _get("https://fonts.googleapis.com/css2?family=%s:wght@400;700"
               "&display=block" % fam)
    chosen = pick(parse_css(css))
    if not chosen:
        return 0, "the font server returned no usable file"

    written = 0
    for suffix, url in chosen:
        blob = _get(url, binary=True)
        ext = url.rsplit(".", 1)[-1].lower()
        os.makedirs(OUT, exist_ok=True)
        with open(os.path.join(OUT, "%s-%s.%s" % (key, suffix, ext)), "wb") as f:
            f.write(blob)
        written += 1
    return written, None


def report(fonts):
    """What is covered and what is not. Answers the only question that matters:
    can a person pick any face in the studio and get that face in the PDF."""
    web = [k for k, f in sorted(fonts.items()) if f.get("g")]
    system = [k for k, f in sorted(fonts.items()) if not f.get("g")]
    missing = []
    print("Webfont families in assets/fonts.json: %d" % len(web))
    for key in web:
        state = covered(key)
        print("  %-16s %s" % (key, state or "NOT COVERED"))
        if not state:
            missing.append(key)
    if system:
        print("System faces, nothing to fetch: %s" % ", ".join(system))
    print("")
    if missing:
        print("%d of %d covered. These would fall back to the font server, and "
              "--pdf will refuse where it cannot be reached:" % (len(web) - len(missing), len(web)))
        print("  %s" % " ".join(missing))
        print("Run: python3 scripts/fetch_fonts.py")
        return 1
    print("All %d covered. Every face the studio offers will print, on any machine, "
          "with or without a network." % len(web))
    return 0


def main(argv):
    fonts = families()
    if "--check" in argv or "--verify" in argv:
        return report(fonts)

    keys = [a for a in argv if not a.startswith("-")] or sorted(fonts)
    unknown = [k for k in keys if k not in fonts]
    if unknown:
        sys.stderr.write("not in assets/fonts.json: %s\n  known: %s\n"
                         % (", ".join(unknown), ", ".join(sorted(fonts))))
        return 2

    total = 0
    failed = []
    for key in keys:
        try:
            n, note = fetch(key, fonts[key])
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as exc:
            print("%-16s could not be fetched: %s" % (key, exc))
            failed.append(key)
            continue
        print("%-16s %s" % (key, note if note else
                            "%d file%s" % (n, "" if n == 1 else "s")))
        total += n

    print("")
    print("%d font file%s in %s" % (total, "" if total == 1 else "s", OUT))
    if failed:
        print("")
        print("%d famil%s could not be reached: %s"
              % (len(failed), "y" if len(failed) == 1 else "ies", " ".join(failed)))
        print("Run this again where the font server is not blocked, or download each "
              "family from fonts.google.com and drop the files in as "
              "<key>-400.woff2 and <key>-700.woff2. A single variable file goes in "
              "as <key>-variable.ttf.")
    print("")
    return report(fonts)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
