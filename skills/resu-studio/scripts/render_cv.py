#!/usr/bin/env python3
"""Render cv-<variant>.md to a self-contained, printable HTML page.

    python3 render_cv.py <cv.md> [--layout sidebar-dark] [--palette forest]
                                 [--typeset mixed] [--skills bars]
                                 [--skills-by "Group=bars;Group=chips"] [--gap normal]
                                 [--hide-groups "Group;Group"]
                                 [--skills-order "A;B;C"] [--skills-place "A=main"]
                                 [--group own]
                                 [--no-legend] [--order ...] [--out FILE]
    python3 render_cv.py <cv.md> --gallery [--outdir DIR]
    python3 render_cv.py --list

The contract, enforced rather than promised:

  * Reads the markdown and nothing else.
  * Adds nothing. Every line on the page came from the markdown.
  * Drops nothing. Source content lines and lines accounted for are counted and
    compared, and the file is not written if they differ.
  * Never clips. No fixed heights, no overflow hidden, no absolute positioning of
    content. Long content makes the document taller, never invisible.
  * Preserves levels, brackets and figures exactly as written.

Skins are CSS only. A skin cannot change a word.
"""

import argparse
import base64
import datetime
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, "assets")


def outdir_for(cv_path, asked=None):
    """Where rendered files go.

    The person's own documents folder, resolved by `paths.documents_dir()`, not beside
    whatever markdown happened to be passed in. The skill is installed once per person
    and the markdown can live anywhere on their disk; defaulting to the markdown's
    folder means the skill writes to a different, unpredictable place for every person
    who runs it, and two people running it produce layouts nobody can describe in one
    sentence. One folder, in the same place every time, is something a person can be
    told to open.

    `--pdf-dir` or `--outdir` still win: someone who names a folder means it.
    A skill installed somewhere unwritable falls back to the markdown's folder
    and says so, because refusing to render at all would be worse.
    """
    if asked:
        os.makedirs(asked, exist_ok=True)
        return asked
    # Not inside the skill. A plugin update replaces the skill folder and deletes
    # the old one, so a finished CV kept in here would disappear on a routine
    # update with nothing on screen connecting the two. `paths` resolves the
    # person's own folder instead, and only falls back to inside the skill when
    # there is nowhere better. The folder is still named for what is in it and
    # still sorts to the top: somebody who has never opened a terminal should find
    # their CV first thing on opening it.
    try:
        sys.path.insert(0, HERE)
        import paths
        out = paths.documents_dir()
    except Exception:
        out = os.path.join(ROOT, "_Your Documents Are Here")
    # Asked by permission, not by writing a test file. The first version created a
    # probe and deleted it, which reported "not writable" on any filesystem that
    # allows writing but not deleting — and left a stray file behind each time it
    # was wrong.
    try:
        os.makedirs(out, exist_ok=True)
        if not os.access(out, os.W_OK):
            raise OSError("not writable")
        return out
    except OSError:
        fallback = os.path.dirname(os.path.abspath(cv_path))
        sys.stderr.write("%s is not writable, so this wrote to %s instead.\n"
                         % (out, fallback))
        return fallback

# Which sections sit in the sidebar when nobody has said. Any skills section joins
# them whatever it is headed, which is what the studio does with its own default, so a
# CV headed TECHNICAL SKILLS is previewed and printed in the same column. --order
# still wins over all of it.
ASIDE_SECTIONS = ("key skills", "skills", "education", "training and certifications",
                  "training & certifications", "certifications", "eligibility")


# ---------------------------------------------------------------- parsing

_MONTHS = ("jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec")


def _is_date_line(t):
    """Is this line only dates?

    Almost nobody writes `### Title | 2023 to present`. They put the dates on the
    line under the heading, which used to be read as the first scope paragraph: the
    date printed in body text, it could not be styled as a date, and there was no
    date line to point at or correct.

    The test is deliberately strict — take out years, month names and the words that
    join two dates, and a real date line has nothing left. A scope sentence that
    happens to mention a year still has its own words in it and is left alone.
    """
    t = (t or "").strip()
    if not t or len(t) > 60 or t.endswith("."):
        return False
    if not re.search(r"(19|20)\d{2}|\b(present|current|ongoing|to date)\b", t, re.I):
        return False
    rest = re.sub(r"(19|20)\d{2}", " ", t)
    rest = re.sub(r"\b(%s)[a-z]*\b" % _MONTHS, " ", rest, flags=re.I)
    rest = re.sub(r"\b(to|until|till|and|present|current|currently|now|ongoing|date|"
                  r"since|from)\b", " ", rest, flags=re.I)
    return not re.sub(r"[\s,\-\u2013\u2014/|()\.]+", "", rest)


def parse(md):
    doc = {"name": "", "contact": [], "sections": [], "contact_src": 0}
    section = role = None
    lines = md.replace("\r\n", "\n").split("\n")
    i, n = 0, len(lines)

    def prose(start):
        buf, j = [], start
        while j < n:
            t = lines[j].strip()
            if (not t or t.startswith("#") or t.startswith("- ") or t.startswith("* ")
                    or re.match(r"^\*\*(.+?):\*\*", t)
                    or re.match(r"^(-{3,}|\*{3,})$", t)):
                break
            buf.append(t)
            j += 1
        return " ".join(buf), j

    while i < n:
        line = lines[i].strip()
        if not line or re.match(r"^(-{3,}|\*{3,})$", line):
            i += 1
            continue
        if line.startswith("# ") and not doc["name"]:
            doc["name"] = line[2:].strip()
            i += 1
            continue
        if line.startswith("## "):
            section = {"title": line[3:].strip(), "blocks": []}
            doc["sections"].append(section)
            role = None
            i += 1
            continue
        if line.startswith("### "):
            head = line[4:].strip()
            title, dates = head, ""
            if "|" in head:
                title, dates = [p.strip() for p in head.rsplit("|", 1)]
            i += 1
            # A date line taken off its own line is a content line of the markdown, so
            # it has to be counted as one. Without this the source count and the
            # accounted-for count differ by one per role and the guard below refuses to
            # write a CV whose only sin is putting the dates where most people put them.
            datesrc = 0
            if not dates:
                j = i
                while j < n and not lines[j].strip():
                    j += 1
                if j < n and _is_date_line(lines[j]):
                    dates = lines[j].strip()
                    datesrc = 1
                    i = j + 1
            role = {"kind": "role", "title": title, "dates": dates,
                    "scope": [], "bullets": [], "src": datesrc}
            (section or _floating(doc))["blocks"].append(role)
            continue
        if line.startswith("- ") or line.startswith("* "):
            # A bullet may be wrapped across several lines. Markdown says the
            # continuation belongs to the bullet; taking only the first line left the
            # rest as a loose paragraph, and — because the paragraph branch closes the
            # bullet list — every bullet after it lost its marker too. One long bullet
            # could turn three bullets into one bullet and two stray sentences, and
            # the line count still balanced, so nothing said so.
            item = line[2:].strip()
            more, j = prose(i + 1)
            if more:
                item = (item + " " + more).strip()
            used = max(1, j - i)
            if role is not None:
                role["bullets"].append(item)
                role["src"] += used
            else:
                (section or _floating(doc))["blocks"].append(
                    {"kind": "item", "text": item, "src": used})
            i = j if more else i + 1
            continue
        m = re.match(r"^\*\*(.+?):\*\*\s*(.*)$", line)
        if m and section:
            text, j = m.group(2).strip(), i + 1
            # A plain line written under a labelled line is its own line, not more of
            # that line. Swallowing it read `**Tools:** Excel (Master)` followed by
            # `Stakeholder engagement; Report writing` as one skills line, and the
            # first bracket then took the next words into itself: two real skills
            # disappeared inside `Excel (Master, Stakeholder engagement)`. The count
            # still balanced, because the lines were counted and then merged, so
            # nothing said a word had changed.
            #
            # The one case where the merge is right is a list that is plainly
            # unfinished: a long skills line broken over two lines ends the first one
            # on a semicolon or a comma. That still joins, and nothing else does.
            if text.endswith((";", ",")):
                more, j = prose(j)
                if more:
                    text = (text + " " + more).strip()
            section["blocks"].append({"kind": "labelled", "label": m.group(1).strip(),
                                      "text": text, "src": j - i})
            role = None
            i = j
            continue
        if section is None:
            # each line of the contact block is its own line on the page, so it can be
            # rewritten or taken off a version on its own
            doc["contact"].append(line)
            doc["contact_src"] += 1
            i += 1
            continue
        text, j = prose(i)
        used = j - i
        if role is not None and not role["bullets"]:
            role["scope"].append(text)
            role["src"] += used
        else:
            section["blocks"].append({"kind": "para", "text": text, "src": used})
            role = None
        i = j
    return doc


SIGNOFFS = ("yours sincerely", "yours faithfully", "kind regards", "regards",
            "sincerely", "best regards", "many thanks", "with thanks")


def parse_letter(md, doc):
    """A cover letter in plain markdown, read by shape rather than by markup.

    Blocks separated by blank lines. The first is the letterhead and is ignored
    here, because the letter wears the CV's own name and contact block. Then a
    date on its own, then who it is addressed to, then a salutation ending in a
    comma, then the body, then a sign-off and a name.
    """
    blocks, buf = [], []
    for raw in md.replace("\r\n", "\n").split("\n"):
        t = raw.strip()
        if t:
            buf.append(t)
        elif buf:
            blocks.append(buf)
            buf = []
    if buf:
        blocks.append(buf)

    out = {"date": "", "to": [], "sal": "", "paras": [], "close": "", "sign": ""}
    if not blocks:
        return out
    rest = blocks[1:]                      # block 0 is the letterhead

    def is_date(b):
        return len(b) == 1 and re.match(
            r"^\d{1,2}\s+[A-Za-z]+\s+\d{4}$|^[A-Za-z]+\s+\d{1,2},?\s+\d{4}$", b[0])

    def is_sal(b):
        return len(b) == 1 and b[0].endswith(",") and len(b[0]) < 90 \
            and not b[0].lower().startswith(SIGNOFFS)

    i = 0
    if i < len(rest) and is_date(rest[i]):
        out["date"] = rest[i][0]
        i += 1
    while i < len(rest) and not is_sal(rest[i]):
        out["to"].extend(rest[i])
        i += 1
    if i < len(rest):
        out["sal"] = rest[i][0]
        i += 1
    while i < len(rest):
        line = " ".join(rest[i])
        if line.lower().startswith(SIGNOFFS):
            out["close"] = line
            i += 1
            if i < len(rest):
                out["sign"] = " ".join(rest[i])
            break
        out["paras"].append(line)
        i += 1
    return out


def letter_meta_html(L):
    out = []
    if L["date"] and not d_removed("cover-letter/date"):
        out.append(_tag("p", "ldate", "cover-letter/date",
                        d_text("cover-letter/date", L["date"])))
    to = []
    for n, t in enumerate(L["to"]):
        i = "cover-letter/to%d" % n
        if not d_removed(i):
            to.append(_tag("p", "", i, d_text(i, t)))
    if to:
        out.append('<div class="lto">%s</div>' % "".join(to))
    return "".join(out)


def letter_body_html(L):
    out = []

    def put(cls, i, text):
        if not d_removed(i):
            out.append(_tag("p", cls, i, d_text(i, text)))
        for k, t in enumerate(d_adds(i)):
            _aid = "%s/+%d" % (i, k)
            if d_removed(_aid):
                d_note("removed", _aid, t)
                continue
            out.append(_tag("p", "lp added", "%s/+%d" % (i, k), t))
            d_note("added", "%s/+%d" % (i, k), t)

    if L["sal"]:
        put("lsal", "cover-letter/sal", L["sal"])
    for n, t in enumerate(L["paras"]):
        put("lp", "cover-letter/p%d" % n, t)
    if L["close"]:
        put("lclose", "cover-letter/close", L["close"])
    if L["sign"]:
        put("lsign", "cover-letter/sign", L["sign"])
    return "".join(out)


def _floating(doc):
    if not doc["sections"] or doc["sections"][-1]["title"] != "":
        doc["sections"].append({"title": "", "blocks": []})
    return doc["sections"][-1]


def count_source(md):
    n = 0
    for raw in md.replace("\r\n", "\n").split("\n"):
        t = raw.strip()
        if not t or t.startswith("#") or re.match(r"^(-{3,}|\*{3,})$", t):
            continue
        n += 1
    return n


def count_doc(doc):
    n = doc.get("contact_src", 0)
    for s in doc["sections"]:
        for b in s["blocks"]:
            n += b.get("src", 1)
    return n


def inline(text):
    t = html.escape(text)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\w)\*(?!\s)(.+?)(?<!\s)\*(?!\w)", r"<em>\1</em>", t)
    return t


# ---------------------------------------------------------------- skills

LEVELS = {"master": 5, "advanced": 4, "intermediate": 3,
          "working knowledge": 2, "exposure": 1}
LEVEL_ORDER = ["Master", "Advanced", "Intermediate", "working knowledge", "exposure"]
SKILL_MODES = ("list", "bars", "dots", "rings", "chips", "columns")
GROUPINGS = ("own", "discipline", "strength")

GAPS = {"tight": "5px", "normal": "9px", "airy": "15px"}

OPTS = {"skills": "list", "skills_by": {}, "hide": set(), "gap": "normal",
        "group_order": [], "group_place": {},
        "group": "own", "legend": True, "order": None}

HIDDEN = []   # what --hide-groups actually took off the page, for the report
EMBEDDED = []  # font files carried inside the document, so the PDF step can say so


def mode_for(label):
    """Each group may be drawn its own way. --skills is only the default."""
    return OPTS["skills_by"].get((label or "").strip().lower(), OPTS["skills"])


def slug(t):
    return re.sub(r"[^a-z0-9]+", "-", (t or "").strip().lower()).strip("-")


def is_skills(title):
    """Is this heading the skills section?

    Any heading with the word skill in it, which is exactly what studio.html and
    build_studio.py both do. Matching only KEY SKILLS and SKILLS meant a CV headed
    TECHNICAL SKILLS was drawn as skills in the studio and printed here as plain
    labelled lines, under a different id on each side, so every decision the person
    took about one of those lines landed on an id this file never built.

    The id prefix the groups themselves carry is unchanged: it is still key-skills,
    the same one build_studio.py hands the studio, so the two sides still agree.
    """
    return "skill" in (title or "").strip().lower()


def split_items(text):
    """One skills line becomes its items. The raw wording is always kept."""
    out = []
    for raw in [x.strip() for x in text.split(";")]:
        if not raw:
            continue
        name, level, extra = raw, None, ""
        m = re.match(r"^(.*?)\s*\(([^()]*)\)(.*)$", raw)
        if m:
            head, inside, tail = m.group(1).strip(), m.group(2).strip(), m.group(3).strip(" ,")
            parts = [x.strip() for x in inside.split(",")]
            if parts and parts[0].lower() in LEVELS:
                level, name = parts[0], head
                bits = [x for x in parts[1:] if x] + ([tail] if tail else [])
                extra = ", ".join(bits)
        out.append({"raw": raw, "name": name, "level": level, "extra": extra})
    return out


def _fonts():
    path = os.path.join(ASSETS, "fonts.json")
    if not os.path.isfile(path):
        return {}, {}
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    return d.get("fonts", {}), d.get("sizes", {})


def _face_for(stack):
    """The fonts.json entry a finished CSS stack came from, or None.

    Matched on the stack itself, so it answers the same whether the face arrived
    from the typeset in skins.json or from --head-font on the command line. A stack
    nobody declared, or one of the system faces that needs no file, gives None and
    nothing is embedded for it.
    """
    if not stack:
        return None
    fonts, _sz = _fonts()
    want = " ".join(stack.split())
    for key, f in fonts.items():
        if " ".join((f.get("css") or "").split()) == want:
            out = dict(f)
            out["_key"] = key
            return out
    return None


def _used_faces(head_stack, body_stack):
    """(key, entry) for each distinct face on this page, heading face first."""
    out, seen = [], set()
    for stack in (head_stack, body_stack):
        f = _face_for(stack)
        if f and f["_key"] not in seen:
            seen.add(f["_key"])
            out.append((f["_key"], f))
    return out


def _family_name(f):
    """The face's own name, as CSS has to spell it in an @font-face rule."""
    first = (f.get("css") or "").split(",")[0].strip()
    return first.strip("'\"")


_FONT_EXTS = ("woff2", "woff", "ttf", "otf")


def _font_weight_of(parts):
    """The numeric weight a filename is claiming, or None.

    Google's own downloads say `regular` and `700`; a Google Fonts zip says
    `Regular` and `Bold`; the helper site says `v33-latin-regular` and
    `v33-latin-700`, and hands over every weight in between. All of them are read,
    at the weight they actually are, so that picking the file is a choice rather
    than an accident of alphabetical order.
    """
    for p in parts:
        if p.isdigit() and 100 <= int(p) <= 900:
            return int(p)
    for word, weight in (("thin", 100), ("extralight", 200), ("light", 300),
                         ("regular", 400), ("normal", 400), ("book", 400),
                         ("roman", 400), ("medium", 500), ("semibold", 600),
                         ("demibold", 600), ("bold", 700), ("extrabold", 800),
                         ("black", 900), ("heavy", 900)):
        if word in parts:
            return weight
    return None


def _font_files_loose(key, folder):
    """Fall back to reading the folder when no file carries the exact expected name.

    Fonts arrive named however whoever downloaded them was given them, and a face
    that is present but spelled differently is indistinguishable, to the rest of
    this file, from a face that is absent. That silence is the whole problem: it
    turns "the fonts are in the folder" into "the PDF export refuses", with nothing
    on screen connecting the two.

    A folder often holds five or six weights. The body wants 400 and the bold wants
    700, so those are taken exactly where they exist and by nearest weight where
    they do not — never by whichever file happened to sort first, which is how a CV
    ends up set in Medium and nobody can say why.
    """
    if not os.path.isdir(folder):
        return []
    variable, seen = None, {}
    for name in sorted(os.listdir(folder)):
        stem, _dot, ext = name.rpartition(".")
        ext = ext.lower()
        if ext not in _FONT_EXTS or not stem.lower().startswith(key.lower() + "-"):
            continue
        parts = set(re.split(r"[-_. ]+", stem[len(key) + 1:].lower()))
        if parts & {"italic", "oblique"}:
            continue
        rank = _FONT_EXTS.index(ext)          # woff2 beats woff beats ttf beats otf
        path = os.path.join(folder, name)
        if parts & {"variable", "wght", "vf"}:
            if variable is None or rank < variable[0]:
                variable = (rank, path)
            continue
        weight = _font_weight_of(parts)
        if weight is None:
            weight = 400                      # an unqualified file is the regular
        if weight not in seen or rank < seen[weight][0]:
            seen[weight] = (rank, path)
    if variable is not None:
        return [("100 900", variable[1])]
    if not seen:
        return []
    out, used = [], set()
    for want in (400, 700):
        pick = min(seen, key=lambda w: (abs(w - want), w))
        if pick in used:
            continue
        used.add(pick)
        out.append((want, seen[pick][1]))
    return out


def _font_files(key):
    """Any bundled weights for one face, as (weight, path).

    Named `<key>-400.woff2` and `<key>-700.woff2` in `assets/fonts/`. .ttf and .otf
    are read too, so a family downloaded from Google's own zip drops straight in.
    Anything else in the folder that starts with the face's key is read as well, so
    a download named the way the source named it still counts as bundled.
    """
    # A variable file covers every weight on its own, so it is looked for first and
    # declared as a range. Asking a variable face for 400 and 700 as two fixed rules
    # gets one real weight and one the browser fakes by smearing it.
    folder = os.path.join(ASSETS, "fonts")
    for ext in _FONT_EXTS:
        path = os.path.join(folder, "%s-variable.%s" % (key, ext))
        if os.path.isfile(path):
            return [("100 900", path)]
    out = []
    for weight in (400, 700):
        for ext in _FONT_EXTS:
            path = os.path.join(folder, "%s-%d.%s" % (key, weight, ext))
            if os.path.isfile(path):
                out.append((weight, path))
                break
    return out or _font_files_loose(key, folder)


_MIME = {"woff2": "font/woff2", "woff": "font/woff",
         "ttf": "font/ttf", "otf": "font/otf"}


def _font_faces(used):
    """@font-face rules carrying the actual font files, base64, inside the document.

    This is what makes the PDF trustworthy. A page that names its typefaces and
    fetches them from a font server prints correctly only where that server is
    reachable; everywhere else the browser quietly substitutes, the metrics change,
    the page breaks move and the file still looks finished. Carrying the bytes means
    the document renders the same on a machine with no network at all, which is
    where PDFs usually get made.

    Nothing is invented: a face with no file bundled is left to the link below.
    """
    css = []
    for key, f in used:
        files = _font_files(key)
        if not files:
            continue
        name = _family_name(f)
        for weight, path in files:
            # A font file that is there and cannot be read is a permission problem or
            # a truncated download, and it used to come out as an uncaught error
            # halfway through building the page. The face is left out and named, and
            # the rest of the document is still produced.
            try:
                with open(path, "rb") as fh:
                    blob = base64.b64encode(fh.read()).decode("ascii")
            except OSError as exc:
                sys.stderr.write("could not read the font file %s (%s), so %s at "
                                 "weight %s is not carried in the document and the "
                                 "printing machine will have to find it.\n"
                                 % (path, exc, name, weight))
                continue
            ext = path.rsplit(".", 1)[-1].lower()
            css.append("@font-face{font-family:'%s';font-style:normal;"
                       "font-weight:%s;font-display:block;"
                       "src:url(data:%s;base64,%s) format('%s')}"
                       % (name, weight, _MIME.get(ext, "font/woff2"), blob,
                          "truetype" if ext in ("ttf", "otf") else ext))
            EMBEDDED.append("%s %s" % (name, weight))
    return "<style>%s</style>" % "".join(css) if css else ""


def _font_link(head, body, used=()):
    """Fetch only the families this page is actually set in.

    Skipped entirely for any face already carried in the document by `_font_faces`:
    a link that duplicates an embedded face is a network request that can only
    make things worse.
    """
    have = {k for k, _f in used if _font_files(k)}
    fams = []
    for key, f in ((head or {}).get("_key"), head), ((body or {}).get("_key"), body):
        if f and f.get("g") and f["g"] not in fams and key not in have:
            fams.append(f["g"])
    if not fams:
        return ""
    return ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?%s'
            '&display=swap">'
            % "&".join("family=%s:wght@400;700" % g for g in fams))


def _regroup_map():
    path = os.path.join(ASSETS, "regroup.json")
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as f:
        return list(json.load(f).get("discipline", {}).items())


def _reorder(groups):
    """Put the groups in the order --skills-order names. Anything it does not
    name keeps its own position at the end."""
    if not OPTS["group_order"]:
        return groups
    want = [x.strip().lower() for x in OPTS["group_order"]]
    left = list(groups)
    out = []
    for n in want:
        for g in list(left):
            if g["label"].strip().lower() == n:
                out.append(g)
                left.remove(g)
                break
    return out + left


_DUPS_SAID = set()


def _ids(groups):
    """Give every group an id of its own.

    Two `**Tools:**` lines both slugged to `key-skills/tools`, so one decision taken
    about one of them was applied to both, and every unlabelled line collapsed onto
    the same empty id. The first group with a heading keeps the id it has always had,
    so decisions already recorded against it still land; a second one carries its
    occurrence number.
    """
    seen, dup = {}, []
    for n, g in enumerate(groups):
        s = slug(g["label"])
        if not s:
            g["gid"] = "key-skills/group-%d" % (n + 1)
            continue
        seen[s] = seen.get(s, 0) + 1
        g["gid"] = ("key-skills/" + s if seen[s] == 1
                    else "key-skills/%s-%d" % (s, seen[s]))
        if seen[s] == 2:
            dup.append(g["label"])
    for label in dup:
        if label.lower() not in _DUPS_SAID:
            _DUPS_SAID.add(label.lower())
            sys.stderr.write("two skills groups are both headed %r. The second one is "
                             "addressed as %s, so a decision about one is not applied "
                             "to the other.\n"
                             % (label, "key-skills/%s-2" % slug(label)))
    return groups


def skill_groups(blocks):
    groups = []
    for b in blocks:
        if b["kind"] == "labelled":
            groups.append({"label": b["label"], "orig": b["text"],
                           "items": split_items(b["text"])})
        elif b["kind"] in ("item", "para"):
            groups.append({"label": "", "orig": b["text"],
                           "items": split_items(b["text"])})

    if OPTS["group"] == "strength":
        allit = [i for g in groups for i in g["items"]]
        out = []
        for lv in LEVEL_ORDER:
            it = [i for i in allit if (i["level"] or "").lower() == lv.lower()]
            if it:
                out.append({"label": lv[0].upper() + lv[1:], "items": it,
                            "orig": "; ".join(x["raw"] for x in it)})
        rest = [i for i in allit if not i["level"]]
        if rest:
            out.append({"label": "Also worked with", "items": rest,
                        "orig": "; ".join(x["raw"] for x in rest)})
        return _ids(_reorder(out))

    if OPTS["group"] == "discipline":
        m = _regroup_map()
        if not m:
            sys.stderr.write("no assets/regroup.json, so --group discipline "
                             "falls back to the headings in your markdown\n")
            return _ids(_reorder(groups))
        out, used = [], set()
        for label, srcs in m:
            it = []
            for src in srcs:
                for g in groups:
                    if g["label"].strip().lower() == src.strip().lower():
                        it += g["items"]
                        used.add(g["label"].strip().lower())
            if it:
                out.append({"label": label, "items": it,
                            "orig": "; ".join(x["raw"] for x in it)})
        for g in groups:
            if g["label"].strip().lower() not in used:
                out.append(g)
        return _ids(_reorder(out))

    return _ids(_reorder(groups))


def _legend():
    if not OPTS["legend"]:
        return ""
    return ('<p class="legend">Scale as stated on this CV: %s.</p>'
            % ", ".join(LEVEL_ORDER))


_LEAD_LABEL = re.compile(r"^\s*[A-Za-z][A-Za-z0-9 &/+.'\-]{0,39}?\s*:\s*")


def strip_heading(label, text):
    """Take the heading off the front of the line the editor was seeded with.

    The studio seeds its editor with `Technical: Python (Advanced)` and strips the
    heading again before drawing, because it prints the heading itself. So does this,
    so a line edited there does not come back out of here with its heading printed
    twice.

    The heading that comes off is not always the heading the group carries now. An
    edit written under Technical is matched back to its skills by fingerprint after
    --group has regrouped them, and the group it lands in is called something else, so
    stripping only the current heading printed `Data and analysis: Technical: Python`.
    Whichever heading the text names comes off: the group's own first, and failing
    that any leading `Word:` prefix. Only a plain heading qualifies, so a real skill
    is never eaten: the prefix has to be letters, digits and spaces, at most 40
    characters, with no bracket, semicolon or comma in it, and what is left has to be
    something, or the line is handed back exactly as written.
    """
    text = (text or "").strip()
    if not text:
        return text
    if label:
        m = re.match(r"\s*%s\s*:?\s*" % re.escape(label), text, re.I)
        if m:
            return text[m.end():].strip() or text
    m = _LEAD_LABEL.match(text)
    if m:
        return text[m.end():].strip() or text
    return text


def _level_tail(i):
    """The stated level and anything beside it, as text, for a drawn treatment.

    A bar, a dot or a ring means nothing to the software that reads the file, and
    `references/ats.md` promises the level prints as text beside the drawing. Reading
    only the skill's name dropped the word: `Python (Advanced, 10+ yrs)` extracted as
    `Python (10+ yrs)`, which is a claim the person did not make.
    """
    bits = [x for x in ((i.get("level") or "").strip(), (i.get("extra") or "").strip())
            if x]
    if not bits:
        return ""
    return ' <span style="opacity:.75">(%s)</span>' % inline(", ".join(bits))


def _group_html(g):
    """One group, drawn the way that group was set. Never invents a level."""
    mode = mode_for(g["label"])
    gid = g.get("gid") or ("key-skills/" + slug(g["label"]))
    if d_removed(gid):
        d_note("removed", gid, g["label"])
        return ""

    # Their own wording wins over every treatment, and it is resolved once, here,
    # before the drawing is chosen. It used to be read only by the list and column
    # branches, so a group rewritten in the studio printed its original wording under
    # bars, dots, rings and chips: the tab that claims to be what prints was not what
    # printed, and the only way to catch it was to read the finished file line by line.
    # The heading comes off the front for the same reason the studio takes it off:
    # the heading is printed separately, and leaving it on prints it twice.
    text = strip_heading(g["label"], d_text(gid, g["orig"], g.get("items")))
    items = g["items"] = split_items(text)

    wrap = ' class="sk%s" data-id="%s"' % (d_class(gid), gid)
    head = '<span class="skg">%s</span>' % inline(g["label"]) if g["label"] else ""
    rated = [i for i in items if (i["level"] or "").lower() in LEVELS]
    rest = [i for i in items if (i["level"] or "").lower() not in LEVELS]

    if mode in ("list", "columns"):
        para = ('<p class="lab">%s%s</p>'
                % ('<span class="labname">%s</span>' % inline(g["label"] + ":")
                   if g["label"] else "", inline(text)))
        inner = '<div class="skcols">%s</div>' % para if mode == "columns" else para
        return '<div%s>%s</div>' % (wrap, inner)

    if mode == "chips":
        # the whole line rides on the chip, so nothing written is left off the page
        body = '<div class="chips">%s</div>' % "".join(
            '<b class="l%d">%s</b>' % (LEVELS.get((i["level"] or "").lower(), 0),
                                       inline(i["raw"]))
            for i in items)
        return '<div%s>%s%s</div>' % (wrap, head, body)

    if mode == "rings":
        # The ring carries no digit. A number on its own is the first thing extracted
        # out of the figure, so a screener read "4" before it read the skill, and the
        # level itself was nowhere in the text. The arc says it to the eye and the
        # caption says it in words.
        body = '<div class="skring">%s</div>' % "".join(
            '<figure><div class="rr" aria-hidden="true" '
            'style="background:conic-gradient('
            'var(--ringfill) %d%%, var(--ringtrack) 0)"><b></b></div>'
            '<figcaption>%s%s</figcaption></figure>'
            % (LEVELS[i["level"].lower()] * 20, inline(i["name"]), _level_tail(i))
            for i in rated) if rated else ""
    else:
        rows = []
        for i in rated:
            v = LEVELS[i["level"].lower()]
            if mode == "bars":
                meter = '<span class="skbar"><i style="width:%d%%"></i></span>' % (v * 20)
            else:
                meter = '<span class="skdots">%s</span>' % "".join(
                    '<u class="%s"></u>' % ("on" if k <= v else "")
                    for k in range(1, 6))
            lab = inline(i["name"]) + _level_tail(i)
            rows.append('<div class="skrow %s"><span>%s</span>%s</div>'
                        % ("bar" if mode == "bars" else "dot", lab, meter))
        body = "".join(rows)

    tail = ('<p class="skrest">%s</p>'
            % inline("; ".join(i["raw"] for i in rest))) if rest else ""
    return '<div%s>%s%s%s</div>' % (wrap, head, body, tail)


DECIDE = {"marks": {}, "adds": {}, "sections": [], "order": {}}
APPLIED = []      # what the decisions file actually changed, for the report
REORDERED = {}    # the lists the decisions file put in a different order


def d_removed(i):
    m = DECIDE["marks"].get(i)
    return bool(m and m.get("a") == "remove")


def _skill_fingerprint(items):
    """The skills a group is made of, in a form that survives being regrouped.

    The same as `skillFingerprint` in studio.html: the item names, lowercased and
    sorted, so the answer does not depend on the heading they happen to sit under.
    """
    names = sorted((i.get("name") or "").lower().strip() for i in items or [])
    return "|".join(n for n in names if n)


def d_text(i, fallback, items=None):
    m = DECIDE["marks"].get(i)
    if m and m.get("a") == "edit" and m.get("text"):
        return m["text"]
    # A skills group's id is built from its heading, and --group changes the heading.
    # The studio records the skills an edit was written about for exactly this reason,
    # and follows the fingerprint when the id no longer matches; the copied command
    # emits --group and --decisions together, so this is the ordinary path rather than
    # an edge case. Without it a person's own wording is silently dropped on the way
    # to the PDF.
    if items and str(i).startswith("key-skills/"):
        fp = _skill_fingerprint(items)
        if fp:
            for key, m2 in DECIDE["marks"].items():
                if not str(key).startswith("key-skills/"):
                    continue
                if (isinstance(m2, dict) and m2.get("a") == "edit"
                        and m2.get("text") and m2.get("skills") == fp):
                    return m2["text"]
    return fallback


def d_adds(i):
    return [x.get("text", "") for x in DECIDE["adds"].get(i, []) if x.get("text")]


def _as_index(x):
    """One entry of an order list as a line number, or None if it is not one."""
    if isinstance(x, bool):
        return None
    if isinstance(x, int):
        return x
    if isinstance(x, str) and re.match(r"^-?\d+$", x.strip()):
        return int(x.strip())
    return None


def order_lists(doc):
    """Every list the person can reorder, and how many lines are in each.

    The key is the id the lines themselves carry, which is how the studio writes it:
    `<section-slug>/<role index>` for the bullets of one role, and the bare
    `<section-slug>` for a flat list such as education or training. The slug is the one
    this file derives from the heading, so a CV headed EMPLOYMENT HISTORY is addressed
    as employment-history and one headed PROFESSIONAL EXPERIENCE as
    professional-experience, exactly as the ids print.
    """
    out = {}
    for s in doc["sections"]:
        if s.get("added") or is_skills(s["title"]):
            continue
        sid = slug(s["title"]) or "section"
        ri = flat = 0
        for b in s["blocks"]:
            if b["kind"] == "role":
                out["%s/%d" % (sid, ri)] = len(b["bullets"])
                ri += 1
            else:
                flat += 1
        if flat:
            out[sid] = flat
    return out


def order_faults(order, lists):
    """The one thing wrong with the order in the decisions file, or None.

    An order is a list of the original line numbers, in the order they should print.
    A number listed twice, or one that names no line, is refused rather than quietly
    skipped: skipping it would move a different line, or print one line twice and drop
    another, and the person would have no way of seeing that from the finished page.

    A key naming a list this CV does not have cannot reorder anything, so it is said
    out loud and the render carries on. Refusing there would mean a CV that will not
    print because of a section somebody took out of the markdown.
    """
    for key in sorted(order):
        want = order[key]
        n = lists.get(key)
        if n is None:
            sys.stderr.write("the decisions file asks for an order under %r, and this "
                             "CV has no such list. Nothing was reordered for it.\n"
                             % key)
            continue
        seen = set()
        for x in want:
            i = _as_index(x)
            if i is None:
                return ('order/"%s" lists %r, and every entry has to be the number of '
                        'a line.' % (key, x))
            if not n:
                return ('order/"%s" asks for line %d, and there are no lines under '
                        'that heading to put in an order.' % (key, i))
            if i < 0 or i >= n:
                return ('order/"%s" asks for line %d, and that list has %d line%s, '
                        'numbered 0 to %d. There is no such line to move, so the rest '
                        'would print in an order you did not ask for.'
                        % (key, i, n, "" if n == 1 else "s", n - 1))
            if i in seen:
                return ('order/"%s" names line %d twice. A line cannot print in two '
                        'places, and printing it once would leave a different line '
                        'off the page without saying so.' % (key, i))
            seen.add(i)
    return None


def d_seq(key, n):
    """The order the lines of one list print in.

    Ids never move: b3 is the fourth bullet of the markdown for as long as the markdown
    says so, so a mark, a proposal and a rewrite all stay attached to the line the
    person pointed at. Only the order they are laid out in changes, and that order
    travels in the decisions file under `order`, written by the studio's arrows.

    Anything the list does not name keeps its own place, in its own order, at the end.
    A line can never fall off the page by being forgotten, which is why the count in
    and the count out still balance.
    """
    want = (DECIDE.get("order") or {}).get(key)
    if not want:
        return list(range(n))
    out, seen = [], set()
    for x in want:
        i = _as_index(x)
        if i is None or i < 0 or i >= n or i in seen:
            continue
        seen.add(i)
        out.append(i)
    out += [i for i in range(n) if i not in seen]
    if out != list(range(n)):
        REORDERED[key] = out
    return out


def d_class(i):
    """A coloured edge on a marked line, and only while marking is on."""
    if not OPTS.get("marks"):
        return ""
    m = DECIDE["marks"].get(i)
    return (" mk mk-" + m["a"]) if m else ""


def d_note(kind, i, text):
    APPLIED.append((kind, i, text))


_MOVED_SAID = set()


def place_of(label, section_place):
    """The column a group prints in. Unset means wherever the section itself sits.

    On a layout with no sidebar there is no other column to send a group to. The
    section's own placement is already clamped to the main column there; the group
    override was not, so `--skills-place "Domain=side"` on a one-column layout matched
    no region and the group was filtered off the page altogether, without a word.
    """
    want = OPTS["group_place"].get((label or "").strip().lower(), section_place)
    if want != section_place and not OPTS.get("has_aside", True):
        key = (label or "").strip().lower()
        if key not in _MOVED_SAID:
            _MOVED_SAID.add(key)
            sys.stderr.write("this layout has no sidebar, so the skills group %r stays "
                             "in the main column. --skills-place only does something "
                             "on a layout with a sidebar.\n" % (label or "(unnamed)"))
        return section_place
    return want


def skills_html(blocks, region=None, section_place="main"):
    gs = skill_groups(blocks)
    if region:
        gs = [g for g in gs if place_of(g["label"], section_place) == region]
    if OPTS["hide"]:
        keep = []
        for g in gs:
            if g["label"].strip().lower() in OPTS["hide"]:
                HIDDEN.append((g["label"], len(g["items"])))
            else:
                keep.append(g)
        gs = keep
    if not gs:
        return ""
    scaled = any(mode_for(g["label"]) in ("bars", "dots", "rings") for g in gs)
    return (_legend() if scaled else "") + "".join(_group_html(g) for g in gs)


def ordered(doc):
    """[(section, 'side'|'main')] honouring --order, else the document order."""
    secs = [s for s in doc["sections"] if s["title"] or s["blocks"]]
    if not OPTS["order"]:
        return [(s, "side" if (is_skills(s["title"])
                              or s["title"].strip().lower() in ASIDE_SECTIONS)
                 else "main")
                for s in secs]
    out, used = [], set()
    for token in OPTS["order"]:
        key, _, place = token.partition(":")
        key, place = slug(key), (place.strip() or "main")
        for idx, s in enumerate(secs):
            if idx not in used and slug(s["title"]) == key:
                out.append((s, place))
                used.add(idx)
                break
    for idx, s in enumerate(secs):
        if idx not in used:
            out.append((s, "main"))
    return out


def add_sections(doc):
    """Sections the person added in the workbench. They are not in the markdown, so
    they carry no source lines: they never touch the in/out count and are reported
    separately, under their own heading, as additions."""
    # follow whatever the file does with its own headings
    titles = [x["title"] for x in doc["sections"] if x["title"]]
    shout = bool(titles) and all(t == t.upper() for t in titles)
    for spec in DECIDE.get("sections") or []:
        lines = [x for x in (spec.get("lines") or []) if (x.get("text") or "").strip()]
        if not lines:
            continue
        title = spec.get("title") or "Added section"
        sec = {"title": title.upper() if shout else title,
               "blocks": [{"kind": "bullet", "text": x["text"].strip(),
                           "id": x.get("key"), "src": 0} for x in lines],
               "added": True}
        after = (spec.get("after") or "").strip().lower()
        at = len(doc["sections"])
        if after:
            for idx, s2 in enumerate(doc["sections"]):
                if slug(s2["title"]) == after:
                    at = idx + 1
                    break
        doc["sections"].insert(at, sec)
    return doc


def _tag(tag, cls, i, text):
    c = (cls or "") + d_class(i)
    return '<%s%s data-id="%s">%s</%s>' % (
        tag, (' class="%s"' % c.strip()) if c.strip() else "", i, inline(text), tag)


def _head_parts(doc):
    """The name and each contact line, addressable like any other line, so they can be
    rewritten or taken off a version without touching the markdown."""
    out = []
    if not d_removed("name/0"):
        out.append(_tag("div", "name", "name/0", d_text("name/0", doc["name"])))
    else:
        d_note("removed", "name/0", doc["name"])
    for n, c in enumerate(doc["contact"]):
        i = "contact/%d" % n
        if d_removed(i):
            d_note("removed", i, c)
            continue
        out.append(_tag("div", "contact", i, d_text(i, c)))
        for k, t in enumerate(d_adds(i)):
            _aid = "%s/+%d" % (i, k)
            if d_removed(_aid):
                d_note("removed", _aid, t)
                continue
            out.append(_tag("div", "contact added", "%s/+%d" % (i, k), t))
            d_note("added", "%s/+%d" % (i, k), t)
    return out


def section_html(s, role_wrap="role", region=None, section_place="main"):
    out = []
    sid = slug(s["title"]) or "section"
    if is_skills(s["title"]):
        body = skills_html(s["blocks"], region, section_place)
        if not body:
            return ""
        # the heading stays in the column the section itself sits in; groups sent
        # across print under their own headings rather than repeating it
        if not (region and region != section_place) and s["title"]:
            out.append('<h2 class="sec"><span>%s</span></h2>' % inline(s["title"]))
        out.append(body)
        return "\n".join(out)
    if s["title"]:
        out.append('<h2 class="sec"><span>%s</span></h2>' % inline(s["title"]))
    ri = 0
    two = slug(s["title"]) in OPTS.get("cols2", set())
    if s.get("added"):
        lis = []
        for n, b in enumerate(s["blocks"]):
            i = b.get("id") or ("%s/%d" % (sid, n))
            if d_removed(i):
                continue
            lis.append(_tag("li", "", i, d_text(i, b["text"])))
            d_note("added", i, b["text"])
        if not lis:
            return ""
        out.append('<ul class="bul%s">%s</ul>'
                   % (" cols2" if two else "", "".join(lis)))
        return "\n".join(out)
    # The flat lines of a section are laid out in the order the person put them in.
    # The lines themselves are addressed by their original number, so `education/1` is
    # the second line of the markdown wherever it prints; only the slot it prints in
    # moves, and every line the order does not name still prints, at the end.
    flat = [b for b in s["blocks"] if b["kind"] != "role"]
    fseq, fat = d_seq(sid, len(flat)), 0
    for blk in s["blocks"]:
        if blk["kind"] == "role":
            b = blk
            base = "%s/%d" % (sid, ri)
            ri += 1
            if d_removed(base + "/h"):
                d_note("removed", base + "/h", b["title"])
                continue
            out.append('<div class="%s%s">'
                       % (role_wrap, d_class(base + "/h")))
            out.append('<div class="rolehead">'
                       '<div class="roletitle" data-id="%s/h">%s</div>'
                       % (base, inline(d_text(base + "/h", b["title"]))))
            if not d_removed(base + "/d"):
                out.append('<div class="roledates" data-id="%s/d">%s</div>'
                           % (base, inline(d_text(base + "/d", b["dates"]))))
            out.append('</div>')
            for j, p in enumerate(b["scope"]):
                k = "%s/s%d" % (base, j)
                if d_removed(k):
                    d_note("removed", k, p)
                    continue
                out.append(_tag("p", "scope", k, d_text(k, p)))
            lis = []
            for j in d_seq(base, len(b["bullets"])):
                x = b["bullets"][j]
                k = "%s/b%d" % (base, j)
                if d_removed(k):
                    d_note("removed", k, x)
                else:
                    lis.append(_tag("li", "", k, d_text(k, x)))
                for n, t in enumerate(d_adds(k)):
                    _aid = "%s/+%d" % (k, n)
                    if d_removed(_aid):
                        d_note("removed", _aid, t)
                        continue
                    d_note("added", "%s/+%d" % (k, n), t)
                    lis.append(_tag("li", "added" + (" mk mk-add" if OPTS.get("marks") else ""),
                                    "%s/+%d" % (k, n), t))
            if lis:
                out.append('<ul class="bul">' + "".join(lis) + "</ul>")
            out.append("</div>")
            continue
        bi = fseq[fat]
        b = flat[bi]
        fat += 1
        k = "%s/%d" % (sid, bi)
        if d_removed(k):
            d_note("removed", k, b.get("text", ""))
            continue
        if b["kind"] == "labelled":
            out.append('<p class="lab%s" data-id="%s"><span class="labname">%s</span>%s</p>'
                       % (d_class(k), k, inline(b["label"]),
                          inline(d_text(k, b["text"]))))
        elif b["kind"] == "item":
            out.append(_tag("p", "item", k, d_text(k, b["text"])))
        else:
            out.append(_tag("p", "para", k, d_text(k, b["text"])))
        for n, t in enumerate(d_adds(k)):
            _aid = "%s/+%d" % (k, n)
            if d_removed(_aid):
                d_note("removed", _aid, t)
                continue
            d_note("added", "%s/+%d" % (k, n), t)
            out.append(_tag("p", "item added" + (" mk mk-add" if OPTS.get("marks") else ""),
                            "%s/+%d" % (k, n), t))
    if two and len(out) > 1:
        return out[0] + '<div class="cols2">' + "".join(out[1:]) + "</div>"
    return "\n".join(out)


# ---------------------------------------------------------------- css

BASE = """
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{background:#e6e7ea;color:var(--text);font-family:var(--body);
     font-size:calc(10.3pt * var(--scale));line-height:1.42;
     -webkit-print-color-adjust:exact;print-color-adjust:exact}
#doc{padding:9mm 0}
.sheet{background:var(--paper);width:210mm;height:297mm;margin:0 auto 7mm;
       position:relative;overflow:hidden;display:flex;flex-direction:column;
       box-shadow:0 0 0 1px rgba(20,24,32,.13)}
.sheet:last-child{margin-bottom:0}
.sheet.unpaged,.sheet.grow{height:auto;min-height:297mm}
.grid{flex:1;min-height:0;grid-template-rows:1fr}
.aside,.main{height:100%;min-height:0;overflow:hidden}
.spill{display:none}
.ldate{margin:0 0 14px;color:var(--muted);font-size:calc(9.4pt * var(--scale))}
.lto{margin:0 0 16px}
.lto p{margin:0 0 1px;font-size:calc(9.8pt * var(--scale));line-height:1.4}
.lto p:first-child{font-weight:700;color:var(--accent)}
.lsal{margin:0 0 11px}
.lp{margin:0 0 9px;line-height:1.58;text-align:left}
.lclose{margin:16px 0 0}
.lsign{margin:20px 0 0;font-weight:700;font-family:var(--head);
       font-size:calc(11.5pt * var(--scale))}
.aside .lto{margin-top:14px}
.aside .lto p:first-child{color:inherit}
.aside .ldate{opacity:.8}
.pad,.rest{flex:1;min-height:0;overflow:hidden}
.sheet.unpaged .aside,.sheet.unpaged .main,.sheet.unpaged .pad,.sheet.unpaged .rest,
.sheet.grow .aside,.sheet.grow .main,.sheet.grow .pad,.sheet.grow .rest{
     height:auto;overflow:visible}
.sheet.unpaged .grid,.sheet.grow .grid{grid-template-rows:auto}
.cvhead{margin:0 0 2px}
.pad{padding:15mm 16mm 17mm}
.name{font-family:var(--head);font-size:calc(22pt * var(--scale));font-weight:700;
      line-height:1.1;margin:0 0 5px}
.contact{font-size:calc(8.8pt * var(--scale));color:var(--muted);margin:0 0 2px;
         line-height:1.4}
h2.sec{font-family:var(--head);font-size:calc(9.7pt * var(--scale));font-weight:700;
       letter-spacing:0.090em;text-transform:uppercase;color:var(--accent);
       margin:15px 0 6px;padding-bottom:3px}
.ruled h2.sec{border-bottom:1.3px solid var(--rule)}
.role{margin:0 0 10px;break-inside:avoid-page;page-break-inside:avoid}
.rolehead{display:flex;justify-content:space-between;gap:12px;align-items:baseline}
.roletitle{font-family:var(--head);font-weight:700;font-size:calc(10.9pt * var(--scale))}
.roledates{color:var(--muted);font-size:calc(8.8pt * var(--scale));white-space:nowrap}
.scope{margin:3px 0 5px}
ul.bul{margin:4px 0 0;padding-left:15px}
ul.bul li{margin:0 0 3.4px}
p.lab{margin:0 0 6px}
.labname{font-weight:700;color:var(--accent);display:block;margin-bottom:1px}
p.item{margin:0 0 3px}
p.para{margin:0 0 6px}
/* skills graphics. Nothing here invents a level: a bar, a dot or a ring is
   drawn only where the markdown states one, and everything else prints as text. */
.pad > h2.sec:first-child,.main > h2.sec:first-child,.rest > h2.sec:first-child,
.aside > h2.sec:first-child,.secwrap:first-child h2.sec{margin-top:0}
.cols2{column-count:2;column-gap:9mm}
.cols2 > *{break-inside:avoid}
ul.bul.cols2{padding-left:15px}
.sk{margin:0 0 var(--skgap,9px);break-inside:avoid}
.sk:last-child{margin-bottom:0}
.sk p.lab{margin-bottom:0}
.skg{font-weight:700;color:var(--accent);display:block;
     margin:0 0 calc(var(--skgap,9px) * .34)}
.skrow{display:grid;grid-template-columns:1fr 26mm;gap:5px;align-items:center;
       margin:0 0 2.2px;font-size:calc(9.2pt * var(--scale))}
.skbar{height:4.4px;background:var(--rule);border-radius:3px;overflow:hidden}
.skbar i{display:block;height:100%;background:var(--accent)}
.skdots{display:flex;gap:2.6px;justify-content:flex-end}
.skdots u{width:6px;height:6px;border-radius:50%;background:var(--rule);display:block}
.skdots u.on{background:var(--accent)}
.skrest{font-size:calc(9pt * var(--scale));margin:2px 0 0}
.skring{display:grid;grid-template-columns:repeat(auto-fill,minmax(23mm,1fr));
        gap:3mm 4mm;margin:3px 0 0}
.skring figure{margin:0;text-align:center;min-width:0}
.skring .rr{width:11mm;height:11mm;border-radius:50%;margin:0 auto 2px;
            display:flex;align-items:center;justify-content:center;
            --ringfill:var(--accent);--ringtrack:var(--rule)}
.skring .rr b{background:var(--paper);width:7.6mm;height:7.6mm;border-radius:50%;
              display:flex;align-items:center;justify-content:center;
              font-size:calc(6.6pt * var(--scale));color:var(--accent);font-weight:700}
.skring figcaption{font-size:calc(7.2pt * var(--scale));line-height:1.2}
.chips{display:flex;flex-wrap:wrap;gap:2.4px}
.chips b{font-weight:400;font-size:calc(8.4pt * var(--scale));padding:1.6px 5px;
         border-radius:2px;border:.8px solid var(--rule);background:var(--tint)}
.chips b.l5{background:var(--accent);color:var(--paper);border-color:var(--accent)}
.chips b.l4{background:var(--tint);border-color:var(--accent);font-weight:700}
.legend{font-size:calc(7.6pt * var(--scale));color:var(--muted);margin:1px 0 7px}
.skcols{column-count:2;column-gap:7mm}
.skcols p.lab{break-inside:avoid}
.aside .skcols{column-count:1}
/* marking, and only when --marks is on */
[data-id]{position:relative}
.cvsel{outline:2px solid #2f6f8f;outline-offset:2px;border-radius:2px}
.mk{box-shadow:-7px 0 0 -4px var(--mkc,#999)}
.mk-flag{--mkc:#b07d17}
.mk-rewrite{--mkc:#2f6f8f}
.mk-edit{--mkc:#2e7d52}
.mk-add{--mkc:#2e7d52}
.cvbar{position:absolute;z-index:99;display:flex;gap:2px;padding:3px;background:#fff;
  border:1px solid #c9cfd9;border-radius:3px;box-shadow:0 3px 12px rgba(16,22,32,.22)}
.cvbar button{width:26px;height:24px;padding:0;border:1px solid transparent;background:none;
  border-radius:2px;cursor:pointer;color:#4a5361;display:flex;align-items:center;
  justify-content:center}
.cvbar button:hover{background:#eef2f6;color:#14607f;border-color:#c9cfd9}
@media print{
  /* Save as PDF drops background colour by default in most browsers, which would
     print a dark sidebar as white paper. This is the instruction not to. */
  *{-webkit-print-color-adjust:exact !important;print-color-adjust:exact !important}
  .cvbar,.cvsel{display:none}
  .mk{box-shadow:none}
  html,body{overflow:visible;margin:0;padding:0}
  body{background:#fff}
  /* #doc carries a 1px tail on screen so the last sheet's shadow is not clipped.
     In print that 1px is a whole extra sheet of paper. */
  #doc{padding:0;margin:0;line-height:0}
  /* The sheet stays a flex column when printing. It was switched to display:block
     here so that break-after:page would be honoured, and that quietly destroyed the
     layout: .grid{flex:1} no longer applied, the grid fell back to content height,
     and .aside{height:100%%} resolved against it, so a tinted sidebar stopped where
     its text stopped instead of running the full page. On screen the sheet is flex
     and looks right, which is why this only ever showed up on paper. Chrome honours
     break-after on a flex container, so nothing is lost by keeping it. */
  .sheet{margin:0;box-shadow:none;break-after:page;page-break-after:always;
         display:flex;flex-direction:column;line-height:normal}
  .sheet:last-child{break-after:auto;page-break-after:auto}
  @page{size:A4;margin:0}
}
"""

# Skills inside a narrow column. The label gets the full width and the drawing sits
# under it: a 26mm meter beside a 35% column leaves the label wrapping four deep
# against a bar hanging in the middle of it.
ASIDE_SK = """
.aside .skrow{grid-template-columns:1fr;gap:2px;margin-bottom:5px;text-align:left}
.aside .skrow.dot{grid-template-columns:1fr auto;gap:6px;align-items:center;
                  margin-bottom:2.5px}
.aside .skbar{background:%(track)s;height:5px;width:auto;margin:0}
.aside .skbar i{background:var(--%(ink)s)}
.aside .skdots{justify-content:flex-end}
.aside .skdots u{background:%(track)s}
.aside .skdots u.on{background:var(--%(ink)s)}
.aside .skring{grid-template-columns:repeat(auto-fill,minmax(19mm,1fr))}
.aside .skring .rr{--ringfill:var(--%(ink)s);--ringtrack:%(track)s}
.aside .skring .rr b{background:var(--%(fill)s);color:var(--%(ink)s)}
.aside .skring figcaption{color:var(--%(ink)s)}
.aside .chips b{border-color:var(--%(cm)s);background:transparent;color:var(--%(ink)s)}
.aside .chips b.l5{background:var(--%(ink)s);color:var(--%(fill)s);
                   border-color:var(--%(ink)s)}
.aside .skrest{text-align:left}
"""

L_SIDEBAR_BARE = """
.sheet{background:var(--paper)}
.grid > .aside{border-%(edge)s:1px solid var(--rule)}
"""

L_SIDEBAR = """
%(bg)s
.grid{display:grid;grid-template-columns:%(cols)s;align-items:start}
.aside{padding:15mm 8mm 15mm 13mm;min-width:0;color:var(--%(ink)s);
       font-size:calc(9.3pt * var(--scale))}
.main{padding:15mm 13mm 17mm 9mm;min-width:0}
.grid.right .aside{padding:15mm 13mm 15mm 8mm}
.grid.right .main{padding:15mm 9mm 17mm 13mm}
.aside .name{font-size:calc(17.5pt * var(--scale));color:var(--%(ink)s);
             letter-spacing:0.009em}
.aside .contact{color:var(--%(cm)s);font-size:calc(8.2pt * var(--scale))}
.aside h2.sec{color:var(--%(ink)s);border-bottom:1.2px solid var(--%(cm)s);
              font-size:calc(8.9pt * var(--scale));margin-top:13px}
.aside .labname{color:var(--%(ink)s)}
.aside p.lab,.aside p.item,.aside p.para{color:var(--%(ink)s)}
.aside .roletitle{font-size:calc(9.6pt * var(--scale))}
.aside .roledates{color:var(--%(cm)s)}
.aside .skg{color:var(--%(ink)s)}
.aside .skrow,.aside .skrest,.aside .legend{color:var(--%(ink)s)}
.aside .legend{opacity:.75}
"""
L_SIDEBAR += ASIDE_SK

# Page one has a sidebar, floor to ceiling. Page two onwards does not.
L_SIDEBAR_TOP = """
.grid{display:grid;grid-template-columns:%(cols)s;align-items:stretch}
.aside{background:var(--tint);min-width:0;padding:15mm %(pr)s 12mm %(pl)s}
.main{min-width:0;padding:15mm %(mpr)s 15mm %(mpl)s}
.aside .name{font-size:calc(18pt * var(--scale))}
.sheet:not(:first-child){background:linear-gradient(to %(far)s,
   var(--tint) 0, var(--tint) 8mm, var(--paper) 8mm)}
.rest{padding:15mm 13mm 17mm 13mm}
.sheet:not(:first-child) .rest{padding-%(edge)s:16mm}
"""
L_SIDEBAR_TOP += ASIDE_SK % {"track": "rgba(0,0,0,.11)", "ink": "text",
                             "cm": "muted", "fill": "tint"}

L_BAND = """
.hdr{background:var(--band);color:var(--bandink);padding:14mm 16mm 11mm}
.hdr .name{color:var(--bandink);font-size:calc(25pt * var(--scale));letter-spacing:0.015em}
.hdr .contact{color:var(--bandmuted);font-size:calc(9pt * var(--scale))}
h2.sec{border-bottom:0;position:relative;padding-left:0}
.ruled h2.sec span{background:var(--paper);padding-right:9px;position:relative;z-index:1}
.ruled h2.sec{overflow:hidden}
.ruled h2.sec:after{content:"";position:absolute;top:50%;left:0;width:100%;
                    height:1.2px;background:var(--rule)}
"""

L_SLAB = """
.pad{padding:15mm 16mm 17mm 46mm}
.slab + .pad{padding-top:0}
.slab{background:var(--band);color:var(--bandink);padding:15mm 16mm 12mm 46mm;
      margin-bottom:9mm}
.slab .name{color:var(--bandink);font-size:calc(26pt * var(--scale));
            letter-spacing:-.3px;line-height:1.02}
.slab .contact{color:var(--bandmuted)}
h2.sec{margin-left:-30mm;width:28mm;float:left;text-align:right;border:0;
       font-size:calc(8.6pt * var(--scale));letter-spacing:0.090em;line-height:1.25;
       margin-top:2px}
.secwrap{margin-bottom:9px}
.secwrap:after{content:"";display:table;clear:both}
.roledates{color:var(--accent);font-weight:700}
"""

L_SPINE = """
.pad{padding:16mm 16mm 17mm 40mm}
.headwrap{margin-left:-24mm;border-bottom:3px solid var(--accent);
          padding-bottom:8px;margin-bottom:6px}
.name{font-size:calc(26pt * var(--scale));letter-spacing:-.5px}
h2.sec{margin-left:-24mm;border:0;color:var(--accent);margin-top:16px}
.role{position:relative;border-left:2px solid var(--rule);padding-left:8mm;
      margin-left:0}
.role:before{content:"";position:absolute;left:-5px;top:5px;width:8px;height:8px;
             border-radius:50%;background:var(--accent)}
.rolehead{display:block}
.roledates{display:block;color:var(--accent);font-weight:700;
           font-size:calc(8.3pt * var(--scale));letter-spacing:0.090em;
           text-transform:uppercase;margin-bottom:2px}
"""

L_CARDS = """
.pad{padding:14mm 15mm 16mm}
.headwrap{background:var(--tint);padding:9mm 10mm 7mm;margin:-14mm -15mm 8mm;
          border-bottom:3px solid var(--accent)}
.name{font-size:calc(23pt * var(--scale))}
.role{background:var(--tint);border-left:3.5px solid var(--accent);
      padding:6mm 7mm 5mm;margin:0 0 5mm}
.roletitle{font-size:calc(11.2pt * var(--scale))}
h2.sec{border-bottom:0;color:var(--accent);letter-spacing:0.090em}
"""

L_CLASSIC = """
.pad{padding:18mm 22mm}
.headwrap{text-align:center;border-top:2.5px solid var(--accent);
          border-bottom:1px solid var(--accent);padding:7px 0 9px;margin-bottom:5px}
.name{font-size:calc(22pt * var(--scale));letter-spacing:0.090em;text-transform:uppercase;
      font-weight:400}
.contact{font-size:calc(8.6pt * var(--scale))}
h2.sec{text-align:center;letter-spacing:0.090em;border:0;font-weight:400;
       font-size:calc(9.2pt * var(--scale));margin-top:17px}
h2.sec:after{content:"";display:block;width:30px;height:1.2px;background:var(--accent);
             margin:5px auto 0}
.rolehead{justify-content:center;gap:9px}
.roledates{color:var(--accent)}
.sk{text-align:center}
.chips{justify-content:center}
.skrow{grid-template-columns:1fr 26mm;gap:6px;align-items:center;text-align:left}
.skbar{width:auto;margin:0}
.skdots{justify-content:flex-end}
.skring{grid-template-columns:repeat(auto-fit,23mm);justify-content:center}
.skrest{text-align:left}
"""

L_RAIL = """
.pad{padding:16mm 16mm 17mm 46mm}
.headwrap{margin-left:-30mm;padding-bottom:9px;border-bottom:1px solid var(--rule);
          margin-bottom:9px}
.name{font-size:calc(24pt * var(--scale));letter-spacing:-.4px}
h2.sec{margin-left:-30mm;border:0;color:var(--accent);letter-spacing:0.090em;margin-top:15px}
.role{position:relative;margin-bottom:6px}
.rolehead{display:block}
.roledates{position:absolute;left:-30mm;top:1px;width:26mm;text-align:right;
           color:var(--muted);font-weight:700;line-height:1.3;white-space:normal;
           overflow-wrap:break-word;font-size:calc(8pt * var(--scale))}
.scope{margin-top:2px}
"""

L_BANDS = """
.pad{padding:14mm 15mm 16mm}
.headwrap{margin-bottom:10px}
.name{font-size:calc(23pt * var(--scale))}
h2.sec{background:var(--tint);color:var(--accent);border:0;letter-spacing:0.090em;
       margin:15px -15mm 8px;padding:5px 15mm}
.roledates{color:var(--accent);font-weight:700}
"""

L_HAIRLINE = """
.pad{padding:20mm 24mm 20mm}
.headwrap{margin-bottom:11px}
.name{font-size:calc(20pt * var(--scale));font-weight:400;letter-spacing:0.090em;
      text-transform:uppercase}
.contact{font-size:calc(8.4pt * var(--scale))}
h2.sec{border:0;border-top:1px solid var(--rule);padding-top:7px;margin-top:16px;
       color:var(--muted);letter-spacing:0.090em}
.roletitle{font-weight:700}
.roledates{color:var(--muted)}
"""

L_PANEL = """
.pad{padding:14mm 16mm 17mm}
.headwrap{border:2px solid var(--accent);padding:8mm 9mm 7mm;margin-bottom:9mm;
          text-align:center}
.name{font-size:calc(21pt * var(--scale));letter-spacing:0.090em;text-transform:uppercase;
      font-weight:400}
.contact{font-size:calc(8.6pt * var(--scale))}
h2.sec{border:0;color:var(--accent);letter-spacing:0.090em;margin-top:15px;
       border-left:3px solid var(--accent);padding-left:8px}
.roledates{color:var(--accent);font-weight:700}
"""

L_COMPACT = """
.pad{padding:12mm 13mm 14mm}
.headwrap{display:flex;justify-content:space-between;align-items:flex-end;
          border-bottom:2.5px solid var(--accent);padding-bottom:6px;margin-bottom:3px}
.headwrap .name{font-size:calc(19pt * var(--scale));margin:0}
.headwrap .contacts{text-align:right}
.skillsblock{column-count:2;column-gap:8mm}
.skillsblock p.lab{break-inside:avoid;margin-bottom:4px}
h2.sec{margin-top:11px}
.role{margin-bottom:7px}
"""

# a letter has no section headings, so the layouts that keep a gutter for them give
# the gutter back rather than printing a letter down two thirds of the page
LETTER_FIX = {
    "slab": ".pad{padding-left:16mm}\n.slab{padding-left:16mm}",
    "spine": ".pad{padding-left:16mm}\n.headwrap{margin-left:0}\nh2.sec{margin-left:0}",
    "rail": ".pad{padding-left:16mm}\n.headwrap{margin-left:0}\nh2.sec{margin-left:0}",
}

LAYOUT_CSS = {"sidebar": L_SIDEBAR, "sidebartop": L_SIDEBAR_TOP, "band": L_BAND,
              "slab": L_SLAB, "spine": L_SPINE, "cards": L_CARDS,
              "classic": L_CLASSIC, "compact": L_COMPACT, "rail": L_RAIL,
              "bands": L_BANDS, "hairline": L_HAIRLINE, "panel": L_PANEL}


# ---------------------------------------------------------------- build

def build(doc, layout, palette, typeset, skins, scoped=None, letter=None):
    L = skins["layouts"][layout]
    P = skins["palettes"][palette]
    T = dict(skins["typesets"][typeset])
    FN, SZ = _fonts()
    if OPTS.get("head_font") in FN:
        T["head"] = FN[OPTS["head_font"]]["css"]
    if OPTS.get("body_font") in FN:
        T["body"] = FN[OPTS["body_font"]]["css"]
    if OPTS.get("size") in SZ:
        T["scale"] = SZ[OPTS["size"]]
    kind = L.get("kind", "band")
    scale = T.get("scale", 1.0) * (0.92 if L.get("tight") else 1.0)

    keys = ("accent", "muted", "rule", "band", "bandink", "bandmuted", "tint",
            "paper", "text")
    v = ":root{" + "".join("--%s:%s;" % (k, P.get(k, "#888")) for k in keys)
    v += "--head:%s;--body:%s;--scale:%s;--skgap:%s}" % (
        T["head"], T["body"], scale, GAPS.get(OPTS["gap"], GAPS["normal"]))
    if scoped:
        v = v.replace(":root{", ".%s{" % scoped)

    if kind == "sidebar" and L.get("full"):
        side = L.get("side", "left")
        fill = L.get("fill", "band")
        bare = L.get("fill") == "none"
        if bare:
            fill = "paper"
        bg = ((L_SIDEBAR_BARE % {"edge": "right" if side == "left" else "left"})
              if bare else
              (".sheet{background:linear-gradient(to %s, var(--%s) 0, var(--%s) 35%%,"
               " var(--paper) 35%%)}" % ("right" if side == "left" else "left",
                                         fill, fill)))
        lay = L_SIDEBAR % {
            "bg": bg,
            "dir": "right" if side == "left" else "left", "fill": fill,
            "track": ("rgba(255,255,255,.20)" if fill == "band"
                      else "rgba(0,0,0,.11)"),
            "ink": "bandink" if fill == "band" else "text",
            "cm": "bandmuted" if fill == "band" else "muted",
            "cols": "35% 65%" if side == "left" else "65% 35%"}
    elif kind == "sidebar":
        right = L.get("side", "left") == "right"
        lay = L_SIDEBAR_TOP % {
            "cols": "65% 35%" if right else "35% 65%",
            "edge": "right" if right else "left",
            "far": "left" if right else "right",
            "pr": "13mm" if right else "8mm",
            "pl": "8mm" if right else "13mm",
            "mpr": "9mm" if right else "13mm",
            "mpl": "13mm" if right else "9mm"}
    else:
        lay = LAYOUT_CSS.get(kind, "")

    head_html = "\n".join(_head_parts(doc))
    ruled = bool(L.get("rule"))

    pairs = ordered(doc)
    aside_src, main_src = "", ""
    pk, head_out = "plain", ""
    has_aside = (kind == "sidebar")
    OPTS["has_aside"] = has_aside

    def column(region):
        """Every section feeds one column, except skills, which can feed both.
        A letter has no sections: on a sidebar skin the date and the addressee ride
        in the column with the name, the way a letterhead does."""
        if letter:
            if not has_aside:
                return letter_meta_html(letter) + letter_body_html(letter)
            return letter_meta_html(letter) if region == "side" \
                else letter_body_html(letter)
        out = []
        for sec, place in pairs:
            place = place if has_aside else "main"
            sid = slug(sec["title"])
            # a marker in the main flow saying where a sidebar section belongs if the
            # panel turns out to be too small to hold the whole of it
            if region == "main" and place == "side":
                out.append('<div class="spill" data-spill="%s"></div>' % sid)
            if is_skills(sec["title"]):
                h = section_html(sec, "role", region if has_aside else "main", place)
            elif place == region:
                h = section_html(sec, "role", region, place)
            else:
                h = ""
            if h:
                out.append(h)
        return "\n".join(out)

    if kind == "sidebar":
        pk = "sidebar" if L.get("full") else "sidebartop"
        aside_src = '<div class="cvhead">%s</div>\n' % head_html + column("side")
        main_src = column("main")
    else:
        body = [sec for sec, _p in pairs]
        if kind in ("band", "slab"):
            pk, head_out = kind, head_html
            if kind == "slab" and not letter:
                parts = []
                for s2 in body:
                    h = section_html(s2, "role", "main", "main")
                    if h:
                        parts.append('<div class="secwrap">%s</div>' % h)
                main_src = "\n".join(parts)
            else:
                main_src = column("main")
        elif kind == "compact":
            parts = _head_parts(doc)
            head_out = (parts[0] if parts else "") \
                + '<div class="contacts">%s</div>' % "".join(parts[1:])
            if letter:
                main_src = column("main")
            else:
                sk = [s2 for s2 in body
                      if is_skills(s2["title"])]
                ot = [s2 for s2 in body if s2 not in sk]
                inner = "".join(section_html(s2, "role", "main", "main") for s2 in sk)
                main_src = ('<div class="skcols">%s</div>' % inner) if inner else ""
                main_src += "\n".join(
                    section_html(s2, "role", "main", "main") for s2 in ot)
        else:
            head_out = head_html
            main_src = column("main")

    if letter:
        lay = lay + "\n" + LETTER_FIX.get(kind, "")

    cfg = {"kind": pk, "side": L.get("side", "left"), "ruled": ruled,
           "head": head_out, "headtag": "div", "headcls": "headwrap"}

    # Which named faces this page actually ends up in. The typeset carries a CSS
    # stack rather than a key, and --head-font/--body-font may have replaced it, so
    # the answer is read back off the finished stack rather than off the arguments.
    used = _used_faces(T.get("head"), T.get("body"))
    faces = _font_faces(used)
    link = _font_link(_face_for(T.get("head")), _face_for(T.get("body")), used)
    doc_html = (faces + link + '<div id="src" hidden>'
                + ('<div data-region="aside">%s</div>' % aside_src if aside_src else "")
                + '<div data-region="main">%s</div></div><div id="doc"></div>' % main_src
                + '<script>window.__PAGE__=%s;window.__MARKUP__=%s;</script>'
                % (json.dumps(cfg), "true" if OPTS.get("marks") else "false")
                + '<script>%s</script>' % _paginator()
                + ('<script>%s</script>' % _marker() if OPTS.get("marks") else ""))
    return v + "\n" + lay, doc_html


def _paginator():
    return _asset("paginate.js")


def _marker():
    return _asset("markup.js")


def _asset(name):
    path = os.path.join(ASSETS, name)
    if not os.path.isfile(path):
        return ""
    with open(path, encoding="utf-8") as f:
        return f.read()


PAGINATOR_MISSING = (
    "REFUSING TO WRITE. assets/paginate.js is missing or empty, and it is what puts "
    "the document on the page: every line is written into a hidden block and the "
    "paginator is what moves it onto the sheets. Without it the file opens blank, at "
    "the right size, with nothing on it. Restore assets/paginate.js and run this "
    "again."
)


def paginator_ok():
    """True when there is a paginator to carry. The page is blank without one."""
    return bool(_asset("paginate.js").strip())


def page(css_vars, sheet, title):
    # Without JavaScript nothing moves out of #src, so the page would be blank. This
    # shows the document unpaginated instead: one long column, everything readable.
    return ("<!doctype html><html><head><meta charset=\"utf-8\"><title>%s</title>"
            "<style>%s\n%s</style>"
            "<noscript><style>#src{display:block}#src[hidden]{display:block}"
            "</style></noscript></head><body>%s</body></html>"
            % (html.escape(title), BASE, css_vars, sheet))


# ---------------------------------------------------------------- pdf

def _title_case(name):
    return " ".join(w[:1] + w[1:].lower() for w in (name or "CV").split())


def _proper(text):
    """Sentence the way a person would write it, for a filename they will send.

    A CV heading is usually set in capitals — ALEX MORGAN TAYLOR — and a filename
    in capitals reads as shouting in an inbox. So an all-capitals string is put back
    into ordinary casing. Anything already mixed is left exactly as written, because
    that is where the acronyms live, whatever they are for this person. Guessing is how
    "NHS" becomes "Nhs".
    """
    text = (text or "").strip()
    if not text or any(c.islower() for c in text):
        return text
    # Capitalise each run of letters, not each space-separated word: a surname
    # carries its own boundaries. O'BRIEN-SUZUKI has three runs and three capitals,
    # and splitting on spaces alone would hand back O'brien-suzuki.
    return re.sub(r"[^\W\d_]+",
                  lambda m: m.group(0)[:1] + m.group(0)[1:].lower(), text)


def _safe(part):
    """One filename segment, cleaned up enough to attach to an email as it stands.

    Characters no filesystem accepts come out: a role read off a job pack routinely
    carries a slash — "Policy / Programme Delivery" — and a slash in a filename
    is a directory on every system there is.

    Commas and slashes are dropped rather than turned into another separator. They
    punctuate a job title inside a sentence; in a filename they only compete with the
    " - " that divides the real fields, and a name with three kinds of separator in it
    reads as machine output. What is left is the title as a person would say it aloud.
    """
    part = re.sub(r'[\\/:*?"<>|\r\n\t]+', " ", part or "")
    part = re.sub(r"[,;]+", " ", part)
    part = re.sub(r"\s+", " ", part).strip(" .-")
    return _proper(part)[:100].strip(" .-")


def _role_from(a, letter):
    """The position applied for: given explicitly, or read off the cover letter.

    The letter addresses the role on the first line of its address block, which is
    where a job pack puts it. Someone who has written the letter has already said
    what the role is and should not be asked a second time.
    """
    if getattr(a, "role", None):
        return _safe(a.role)
    if letter and letter.get("to"):
        return _safe(letter["to"][0])
    return ""


def _datestamp(a):
    if getattr(a, "date", None):
        return _safe(a.date)
    return datetime.date.today().strftime("%Y%m%d")


def _pdf_names(doc, outdir, tag, role="", stamp="", employer=""):
    """<Name> - <Role> - <Employer> - <YYYYMMDD> - CV.pdf

    The role, the employer and the date are in the name because these files get sent,
    and a recruiter's inbox is full of documents called Resume.pdf. The employer is
    there because two applications for the same job title, built from the same
    markdown on the same day, otherwise produce one filename and the second one writes
    over the first. A segment with nothing in it is left out rather than printed as an
    empty gap between two hyphens.
    """
    bits = [_safe(doc["name"])]
    if role:
        bits.append(role)
    if employer:
        bits.append(employer)
    if stamp:
        bits.append(stamp)
    bits.append("Cover Letter" if tag == "letter" else "CV")
    return os.path.join(outdir, " - ".join(b for b in bits if b) + ".pdf")


_GENERIC_FAMILIES = ("serif", "sans-serif", "monospace", "system-ui", "cursive",
                     "fantasy", "ui-serif", "ui-sans-serif", "ui-monospace",
                     "ui-rounded", "inherit", "initial", "unset")


def _named_families(stack):
    """The real family names in a CSS stack, with the generic keywords taken out."""
    out = []
    for part in (stack or "").split(","):
        fam = part.strip().strip("'\"").strip()
        if fam and fam.lower() not in _GENERIC_FAMILIES:
            out.append(fam)
    return out


def _wanted_faces(a, skins):
    """The named faces this skin asks for, and whether a file was bundled for each.

    An empty answer means nothing is checked and nothing is embedded, so the PDF
    prints in whatever the machine happens to have. That is fine when the skin asks
    only for a system face, and is a silent failure when it asks for a face nobody
    can find. The two are told apart here and the second one says so out loud, rather
    than letting a substituted CV come out looking finished.
    """
    T = dict(skins["typesets"][a.typeset])
    FN, _sz = _fonts()
    if OPTS.get("head_font") in FN:
        T["head"] = FN[OPTS["head_font"]]["css"]
    if OPTS.get("body_font") in FN:
        T["body"] = FN[OPTS["body_font"]]["css"]
    used = _used_faces(T.get("head"), T.get("body"))
    if not used:
        named = []
        for stack in (T.get("head"), T.get("body")):
            for fam in _named_families(stack):
                if fam not in named:
                    named.append(fam)
        if named:
            sys.stderr.write(
                "WARNING: this skin asks for %s, and no entry in assets/fonts.json "
                "matches the stack it asks with, so no typeface is carried in the "
                "document and none is checked in the PDF. The file will print in "
                "whatever face the printing machine happens to have.\n"
                "  stacks that did not resolve: %s\n"
                "  Fix the typeset in assets/skins.json so its head and body stacks "
                "are copied exactly from a css value in assets/fonts.json, or pass "
                "--head-font and --body-font.\n"
                % (", ".join(named),
                   "; ".join(s for s in (T.get("head"), T.get("body")) if s)))
    return used


def _documents():
    """The small record beside the documents. Never load-bearing: if it cannot be
    imported or written, rendering carries on exactly as before."""
    try:
        sys.path.insert(0, HERE)
        import documents
        return documents
    except Exception:
        return None


def _keep_earlier(dest, role, source, employer=""):
    # The employer is part of what makes two documents the same document. It is passed
    # as a keyword and the call is tried again without it, so this keeps working
    # against a copy of documents.py that has not been given the argument yet.
    d = _documents()
    if not d:
        return None
    try:
        try:
            return d.protect(dest, role, source, employer=employer)
        except TypeError:
            return d.protect(dest, role, source)
    except Exception:
        return None


def _record(path, role, tag, source, employer=""):
    d = _documents()
    if not d:
        return
    kind = "letter" if tag == "letter" else "cv"
    write = getattr(d, "record", None) or getattr(d, "note", None)
    if not write:
        return
    try:
        try:
            write(path, role, kind, source, employer=employer)
        except TypeError:
            write(path, role, kind, source)
    except Exception:
        pass


def write_pdfs(a, doc, letter, skins, cv_html):
    """Print the finished documents, then check the file before handing it over.

    The check is the point. A browser that cannot reach a typeface does not fail: it
    substitutes a face with different metrics, re-flows every line against it, and
    writes a PDF that looks complete and is not the document anybody approved. The
    only way to know is to read the faces back out of the finished file and compare
    them with the faces the skin asked for. When they differ this refuses, the same
    way the line count refuses, because a wrong CV that looks right is the one kind
    of failure the person cannot catch themselves.
    """
    sys.path.insert(0, HERE)
    try:
        import to_pdf
    except ImportError:
        sys.stderr.write("scripts/to_pdf.py is missing, and it is what prints.\n")
        return 2

    browser = to_pdf.find_browser()
    if not browser:
        sys.stderr.write(to_pdf.ADVICE + "\n")
        return 3

    outdir = outdir_for(a.cv, a.pdf_dir)

    # What to print. One --pdf run produces every document it was given, because the
    # two are posted together and a person who has one and not the other has neither.
    jobs = []
    if letter:
        jobs.append(("letter", cv_html))
        # The resume was not built in this run, so build it now, on the same skin.
        del EMBEDDED[:]
        v2, sheet2 = build(doc, a.layout, a.palette, a.typeset, skins, letter=None)
        side = os.path.join(outdir, ".cv-print.html")
        with open(side, "w", encoding="utf-8") as f:
            f.write(page(v2, sheet2, doc["name"] or "CV"))
        jobs.append(("cv", side))
    else:
        jobs.append(("cv", cv_html))

    wanted = _wanted_faces(a, skins)
    role, stamp = _role_from(a, letter), _datestamp(a)
    employer = _safe(getattr(a, "employer", "") or "")
    written = []
    kept = []
    for tag, src in jobs:
        dest = _pdf_names(doc, outdir, tag, role, stamp, employer)
        # Re-rendering the same document overwrites, which is what somebody trying
        # six skins wants. A different advertisement does not: the old file is moved
        # aside under a dated name first, because the two can share a filename and
        # nothing on screen would otherwise say the earlier one had gone.
        aside = _keep_earlier(dest, role, a.cv, employer)
        if aside:
            kept.append(aside)
        try:
            pages = to_pdf.html_to_pdf(src, dest, browser=browser)
        except to_pdf.NoBrowser as exc:
            sys.stderr.write(str(exc) + "\n")
            return 3
        except RuntimeError as exc:
            sys.stderr.write("REFUSING. %s\n" % exc)
            return 1

        missing = _substituted(dest, wanted, to_pdf)
        if missing and not a.pdf_allow_substitute:
            for path, _t in written:
                try:
                    os.remove(path)
                except OSError:
                    pass
            try:
                os.remove(dest)
            except OSError:
                pass
            sys.stderr.write(
                "REFUSING TO HAND OVER A PDF. The skin asks for %s, and the browser "
                "could not load %s, so it substituted another face and re-flowed "
                "every line against different metrics. The file would look finished "
                "and would not be the document you approved.\n"
                "  Carry the faces in the skill and this stops depending on a "
                "network at all. Once, on a machine with internet:\n"
                "    python3 scripts/fetch_fonts.py           # every face the "
                "studio offers\n"
                "    python3 scripts/fetch_fonts.py --check   # confirm all of them "
                "are covered\n"
                "  Or pass --pdf-allow-substitute if a near miss is genuinely fine.\n"
                % (", ".join(_family_name(f) for _k, f in wanted),
                   ", ".join(missing)))
            return 1
        written.append((dest, tag))
        if tag == "letter" and pages > 1:
            sys.stderr.write("the cover letter came out %d pages. It should be one. "
                             "The PDF is written; shorten the letter and run it "
                             "again.\n" % pages)
        print("wrote %s, %d page%s" % (dest, pages, "" if pages == 1 else "s"))

    side = os.path.join(outdir, ".cv-print.html")
    if os.path.exists(side):
        try:
            os.remove(side)
        except OSError:
            pass

    for path, tag in written:
        _record(path, role, tag, a.cv, employer)
    for path in kept:
        print("  kept your earlier document as %s" % os.path.basename(path))
    if written and not role and not employer:
        print("  NOTE: no role and no employer in the filename, so a second "
              "application on the same day would share it. Pass --role \"<the job "
              "title>\" and --employer \"<who it is for>\", or render with --letter, "
              "and each application gets its own file.")
    elif written and role and not employer:
        print("  NOTE: no employer in the filename, so a second application for the "
              "same job title on the same day would share it. Pass --employer "
              "\"<who it is for>\" and each one gets its own file.")

    faces = to_pdf.font_names(written[0][0]) if written else []
    if faces:
        print("  typefaces in the file: %s" % ", ".join(faces))
    print("  printed by %s, so the palette, the meters, the sidebar and the page "
          "breaks are the skin itself rather than a redrawing of it."
          % os.path.basename(browser))
    print("  the text is still text, so a screener can read it.")
    return 0


def _substituted(pdf_path, wanted, to_pdf):
    """Named faces the skin asked for that did not make it into the PDF."""
    if not wanted:
        return []
    got = " ".join(to_pdf.font_names(pdf_path)).lower().replace(" ", "")
    missing = []
    for _key, f in wanted:
        name = _family_name(f).lower().replace(" ", "")
        # Source Sans 3 embeds as SourceSans3; Archivo Narrow as ArchivoNarrow.
        if name not in got:
            missing.append(_family_name(f))
    return missing


# ---------------------------------------------------------------- main

def _decisions_wrong(d):
    """The one thing wrong with a decisions file, said in a sentence, or None.

    This file is routinely hand saved out of a pasted block, so a small shape error is
    likely, and the shape errors all used to arrive as a Python traceback in the middle
    of a render. Each check names the key it is unhappy with, because the person has to
    go and find it in a file they did not write by hand.
    """
    if not isinstance(d, dict):
        return ("the file itself has to be an object with marks, adds and sections in "
                "it, and this one is a %s." % type(d).__name__)

    marks = d.get("marks")
    if marks is not None and not isinstance(marks, dict):
        return "marks has to be an object of id to decision, and it is a %s." \
            % type(marks).__name__
    for key, m in (marks or {}).items():
        if not isinstance(m, dict):
            return ('marks/"%s" has to be an object with an "a" in it, and it is a %s.'
                    % (key, type(m).__name__))

    adds = d.get("adds")
    if adds is not None and not isinstance(adds, dict):
        return "adds has to be an object of id to added lines, and it is a %s." \
            % type(adds).__name__
    for key, lst in (adds or {}).items():
        if not isinstance(lst, list):
            return ('adds/"%s" has to be a list of objects each with a "text", and it '
                    'is a %s.' % (key, type(lst).__name__))
        for x in lst:
            if not isinstance(x, dict):
                return ('one entry under adds/"%s" is a %s, and every entry has to be '
                        'an object with a "text" in it.' % (key, type(x).__name__))

    order = d.get("order")
    if order is not None and not isinstance(order, dict):
        return ("order has to be an object of list id to the line numbers in the order "
                "they should print, and it is a %s." % type(order).__name__)
    for key, want in (order or {}).items():
        if not isinstance(want, list):
            return ('order/"%s" has to be a list of line numbers, and it is a %s.'
                    % (key, type(want).__name__))

    sections = d.get("sections")
    if sections is not None and not isinstance(sections, list):
        return "sections has to be a list of added sections, and it is a %s." \
            % type(sections).__name__
    for n, spec in enumerate(sections or []):
        if not isinstance(spec, dict):
            return ("sections entry %d is a %s, and every entry has to be an object "
                    'with a "title" and a "lines".' % (n + 1, type(spec).__name__))
        lines = spec.get("lines")
        if lines is not None and not isinstance(lines, list):
            return ('the "lines" of sections entry %d has to be a list of objects each '
                    'with a "text", and it is a %s.' % (n + 1, type(lines).__name__))
        for x in lines or []:
            if not isinstance(x, dict):
                return ('one line of sections entry %d is a %s, and every line has to '
                        'be an object with a "text" in it.'
                        % (n + 1, type(x).__name__))
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cv", nargs="?")
    ap.add_argument("--layout", default="sidebar-dark")
    ap.add_argument("--palette", default="forest")
    ap.add_argument("--typeset", default="mixed")
    ap.add_argument("--out",
                    help="the HTML file to write. Default: a name built from the "
                         "markdown, the layout and the palette, in your documents "
                         "folder")
    ap.add_argument("--pdf", action="store_true",
                    help="also print the finished documents to PDF, through a real "
                         "browser, so the file is the skin rather than a redrawing "
                         "of it. With --letter it writes both PDFs.")
    ap.add_argument("--pdf-dir", default=None, dest="pdf_dir",
                    help="where the PDFs go. Default: the same documents folder the "
                         "HTML goes to")
    ap.add_argument("--role", default=None,
                    help="the position applied for, used in the PDF filename. "
                         "Read off the cover letter's address block when there is one")
    ap.add_argument("--employer", default="",
                    help="the employer this version is for, so two applications for "
                         "the same job title do not share a filename")
    ap.add_argument("--date", default=None,
                    help="the date stamp in the PDF filename, written however you "
                         "pass it. Default: today, as YYYYMMDD")
    ap.add_argument("--pdf-allow-substitute", action="store_true",
                    dest="pdf_allow_substitute",
                    help="write the PDF even when a typeface the skin asked for "
                         "could not be loaded and the browser used another")
    ap.add_argument("--gallery", action="store_true")
    ap.add_argument("--outdir")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--skills", default="list", choices=SKILL_MODES,
                    help="default drawing for every skills group")
    ap.add_argument("--skills-by", default=None, dest="skills_by",
                    help="per group, e.g. \"Technical=bars;Languages=chips\". "
                         "Any group not named here uses --skills")
    ap.add_argument("--gap", default="normal", choices=("tight", "normal", "airy"),
                    help="space between skills groups")
    ap.add_argument("--head-font", default=None, dest="head_font",
                    help="the face the headings are set in, from assets/fonts.json")
    ap.add_argument("--body-font", default=None, dest="body_font",
                    help="the face the body text is set in, from assets/fonts.json")
    ap.add_argument("--size", default=None, choices=("small", "normal", "large"),
                    help="overall text size")
    ap.add_argument("--letter", default=None,
                    help="a cover letter in markdown. Renders the letter instead of "
                         "the CV, on the same skin and with the same name and contact "
                         "block, on one page.")
    ap.add_argument("--columns", default=None,
                    help="sections to run in two columns, by slug, comma separated. A "
                         "slug is the heading in lower case with every run of other "
                         "characters turned into one hyphen, so TRAINING AND "
                         "CERTIFICATIONS is training-and-certifications. Only flat "
                         "lists take it: education, training and any section you added.")
    ap.add_argument("--decisions", default=None,
                    help="a cv-decisions.json from the workbench. Applies the lines you "
                         "took off, the wording you rewrote yourself, the lines you "
                         "added and the order you moved them into, and reports every "
                         "one of them")
    ap.add_argument("--marks", action="store_true",
                    help="put the marking toolbar in the rendered page. Off by default, "
                         "so what you print is clean")
    ap.add_argument("--skills-order", default=None, dest="skills_order",
                    help="the skills groups in the order they should print, by their "
                         "exact headings, separated by semicolons. Any heading not "
                         "named keeps its own position at the end")
    ap.add_argument("--skills-place", default=None, dest="skills_place",
                    help="send single groups to the other column, e.g. "
                         "\"Domain=main;Systems and platforms=side\". Only does "
                         "anything on a layout with a sidebar. The Key skills heading "
                         "stays in the column the section itself sits in")
    ap.add_argument("--hide-groups", default=None, dest="hide_groups",
                    help="skills groups to leave off this version, by their exact "
                         "headings, separated by semicolons. Reported in the output, "
                         "never silent")
    ap.add_argument("--group", default="own", choices=GROUPINGS,
                    help="own keeps your headings; discipline uses assets/regroup.json; "
                         "strength regroups by the level each skill states")
    ap.add_argument("--no-legend", dest="legend", action="store_false",
                    help="leave off the line explaining the five steps")
    ap.add_argument("--order", default=None,
                    help="section order and column, e.g. "
                         "profile,key-skills:side,professional-experience,education")
    a = ap.parse_args()

    OPTS["skills"] = a.skills
    OPTS["marks"] = a.marks
    _fn, _sz = _fonts()
    for key, val in (("head_font", a.head_font), ("body_font", a.body_font)):
        if val:
            if val not in _fn:
                sys.stderr.write("unknown font %r. assets/fonts.json lists them: %s\n"
                                 % (val, ", ".join(sorted(_fn))))
                return 2
            OPTS[key] = val
    OPTS["size"] = a.size
    OPTS["gap"] = a.gap
    OPTS["cols2"] = set(slug(x) for x in (a.columns or "").split(",") if x.strip())
    if a.decisions:
        if not os.path.isfile(a.decisions):
            sys.stderr.write("no decisions file at %s\n" % a.decisions)
            return 2
        try:
            with open(a.decisions, encoding="utf-8") as f:
                d = json.load(f)
        except ValueError as exc:
            sys.stderr.write("REFUSING TO WRITE. %s is not valid JSON: %s. It is "
                             "usually a missing comma, a trailing comma or a quote "
                             "that did not get pasted.\n" % (a.decisions, exc))
            return 1
        except OSError as exc:
            sys.stderr.write("REFUSING TO WRITE. %s could not be read: %s\n"
                             % (a.decisions, exc))
            return 1
        wrong = _decisions_wrong(d)
        if wrong:
            sys.stderr.write("REFUSING TO WRITE. In %s, %s\n" % (a.decisions, wrong))
            return 1
        DECIDE["marks"] = d.get("marks") or {}
        DECIDE["adds"] = d.get("adds") or {}
        DECIDE["sections"] = d.get("sections") or []
        DECIDE["order"] = d.get("order") or {}
    if a.skills_order:
        OPTS["group_order"] = [x.strip() for x in a.skills_order.split(";") if x.strip()]
    if a.skills_place:
        for pair in a.skills_place.split(";"):
            label, _, where = pair.partition("=")
            where = where.strip().lower()
            if not label.strip():
                continue
            if where not in ("side", "main"):
                sys.stderr.write("--skills-place takes side or main, not %r\n" % where)
                return 2
            OPTS["group_place"][label.strip().lower()] = where
    if a.hide_groups:
        OPTS["hide"] = set(x.strip().lower() for x in a.hide_groups.split(";") if x.strip())
    if a.skills_by:
        for pair in a.skills_by.split(";"):
            label, _, m = pair.partition("=")
            m = m.strip().lower()
            if not label.strip():
                continue
            if m not in SKILL_MODES:
                sys.stderr.write("unknown skills mode %r in --skills-by\n" % m)
                return 2
            OPTS["skills_by"][label.strip().lower()] = m
    OPTS["group"] = a.group
    OPTS["legend"] = a.legend
    OPTS["order"] = [x.strip() for x in a.order.split(",") if x.strip()] if a.order else None

    with open(os.path.join(ASSETS, "skins.json"), encoding="utf-8") as f:
        skins = json.load(f)

    if a.list:
        for k in ("layouts", "palettes", "typesets"):
            print(k + ":")
            for name, d in skins[k].items():
                print("  %-15s %s" % (name, d["label"]))
        return 0

    if not a.cv:
        ap.error("a cv markdown file is required")
    if not paginator_ok():
        sys.stderr.write(PAGINATOR_MISSING + "\n")
        return 1
    for key, grp in (("layout", "layouts"), ("palette", "palettes"),
                     ("typeset", "typesets")):
        if getattr(a, key) not in skins[grp]:
            sys.stderr.write("unknown %s %r. --list shows them all.\n"
                             % (key, getattr(a, key)))
            return 2

    md = open(a.cv, encoding="utf-8").read()
    doc = parse(md)
    src, got = count_source(md), count_doc(doc)
    # added sections come after the count, so they can never disguise a dropped line
    add_sections(doc)
    if src != got:
        sys.stderr.write("REFUSING TO WRITE. %d content lines in the markdown, %d "
                         "accounted for. Something would have been dropped.\n"
                         % (src, got))
        return 1

    # The order the person put the lines in, checked against the lines that exist
    # before anything is drawn. An order that names a line twice, or names one that is
    # not there, would print one line twice and leave another off, and the count above
    # would still balance, so it is caught here and said in the same voice.
    if DECIDE.get("order"):
        wrong = order_faults(DECIDE["order"], order_lists(doc))
        if wrong:
            sys.stderr.write("REFUSING TO WRITE. In %s, %s\n" % (a.decisions, wrong))
            return 1

    if a.gallery:
        outdir = a.outdir or os.path.join(outdir_for(a.cv), "skins-samples")
        os.makedirs(outdir, exist_ok=True)
        n = 0
        index = []
        for lay in skins["layouts"]:
            for pal in skins["palettes"]:
                v, sheet = build(doc, lay, pal, a.typeset, skins)
                fn = "%s--%s.html" % (lay, pal)
                full = page(v, sheet, "%s / %s" % (lay, pal))
                with open(os.path.join(outdir, fn), "w", encoding="utf-8") as f:
                    f.write(full)
                tile = full.replace("</style>",
                    ".sheet{margin:0 auto;box-shadow:none}</style>", 1)
                index.append((lay, pal, fn, tile))
                n += 1
        rows = "".join(
            '<a class="c" href="%s" target="_blank"><span class="fr">'
            '<iframe srcdoc="%s" scrolling="no" tabindex="-1"></iframe></span>'
            '<span class="cap">%s<br><b>%s</b></span></a>'
            % (fn, html.escape(full, True), skins["layouts"][l]["label"],
               skins["palettes"][pp]["label"])
            for l, pp, fn, full in index)
        idx = ("<!doctype html><html><head><meta charset=\"utf-8\"><title>Skins</title>"
               "<style>body{font:14px/1.5 Arial,sans-serif;background:#f3f3f5;margin:0;"
               "padding:26px}h1{margin:0 0 4px}p.i{color:#555;margin:0 0 22px}"
               ".c{display:inline-block;width:252px;margin:0 16px 26px;text-decoration:none;"
               "color:#222;vertical-align:top}"
               ".fr{display:block;width:252px;height:356px;overflow:hidden;"
               "border:1px solid #c7c7cc;background:#fff;position:relative}"
               ".c iframe{width:794px;height:1123px;border:0;display:block;"
               "pointer-events:none;transform:scale(.3174);transform-origin:0 0;"
               "position:absolute;top:0;left:0}"
               ".c:hover .fr{border-color:#111;box-shadow:0 3px 12px rgba(0,0,0,.22)}"
               ".cap{display:block;padding:7px 2px 0;font-size:12.5px;color:#444}"
               "</style></head><body><h1>%d skins</h1>"
               "<p class=\"i\">Every one rendered from your own CV. Click any tile to "
               "open it full size.</p>%s</body></html>"
               % (n, rows))
        with open(os.path.join(outdir, "index.html"), "w", encoding="utf-8") as f:
            f.write(idx)
        print("wrote %d skins to %s" % (n, outdir))
        print("open %s" % os.path.join(outdir, "index.html"))
        return 0

    letter = None
    if a.letter:
        if not os.path.isfile(a.letter):
            sys.stderr.write("no cover letter at %s\n" % a.letter)
            return 2
        with open(a.letter, encoding="utf-8") as f:
            letter = parse_letter(f.read(), doc)
        if not letter["paras"]:
            sys.stderr.write("REFUSING TO WRITE. %s parsed to no paragraphs. A cover "
                             "letter needs a date, who it is to, a salutation ending "
                             "in a comma, the body, and a sign-off, each separated by "
                             "a blank line.\n" % a.letter)
            return 1

    v, sheet = build(doc, a.layout, a.palette, a.typeset, skins, letter=letter)
    stem = os.path.basename(os.path.splitext(a.letter if a.letter else a.cv)[0])
    # The employer belongs in this name for the same reason it belongs in the PDF's:
    # two applications for the same job title otherwise write over each other.
    emp = slug(getattr(a, "employer", "") or "")
    out = a.out or os.path.join(outdir_for(a.cv),
                                "%s-%s-%s.html" % (stem + ("-" + emp if emp else ""),
                                                   a.layout, a.palette))
    with open(out, "w", encoding="utf-8") as f:
        f.write(page(v, sheet, doc["name"] or "CV"))

    if a.pdf:
        rc = write_pdfs(a, doc, letter, skins, out)
        if rc:
            return rc
    roles = sum(1 for s in doc["sections"] for b in s["blocks"] if b["kind"] == "role")
    bullets = sum(len(b["bullets"]) for s in doc["sections"] for b in s["blocks"]
                  if b["kind"] == "role")
    print("wrote %s" % out)
    if letter:
        n_to = len(letter["to"])
        print("  cover letter: %d paragraph%s, addressed over %d line%s, on the "
              "resume's own skin." % (len(letter["paras"]),
                                      "" if len(letter["paras"]) == 1 else "s",
                                      n_to, "" if n_to == 1 else "s"))
        print("  the name and contact block came from %s, so the two documents "
              "cannot drift apart." % os.path.basename(a.cv))
        print("  open it and check it is one page. A cover letter that runs to two "
              "is a cover letter nobody finishes.")
    gone = [x for x in APPLIED if x[0] == "removed"]
    new = [x for x in APPLIED if x[0] == "added"]
    if not letter:
        # The count is the parse: what the markdown holds and what was accounted for.
        # The decisions file then takes lines off and puts lines on, and saying
        # "nothing added, nothing dropped" one line above a list of exactly that was
        # the summary contradicting itself.
        did = []
        if gone:
            did.append("took %d line%s off" % (len(gone), "" if len(gone) == 1 else "s"))
        if new:
            did.append("added %d line%s" % (len(new), "" if len(new) == 1 else "s"))
        if did:
            print("  %d content lines in, %d out, and then your decisions %s. Every "
                  "one of them is listed below." % (src, got, " and ".join(did)))
        else:
            print("  %d content lines in, %d out. Nothing added, nothing dropped."
                  % (src, got))
    if APPLIED:
        if gone:
            print("  taken off by your decisions: %d line%s"
                  % (len(gone), "" if len(gone) == 1 else "s"))
            for _k, i, t in gone:
                print("    - [%s] %s" % (i, (t or "")[:96]))
        if new:
            print("  added by you: %d line%s"
                  % (len(new), "" if len(new) == 1 else "s"))
            for _k, i, t in new:
                print("    + [%s] %s" % (i, (t or "")[:96]))
        print("  your markdown was not touched. The archive in the workbench holds the "
              "wording of everything above.")
    if REORDERED:
        print("  put in the order you chose: %d list%s"
              % (len(REORDERED), "" if len(REORDERED) == 1 else "s"))
        for key in sorted(REORDERED):
            print("    ~ [%s] now prints as %s"
                  % (key, ", ".join(str(i) for i in REORDERED[key])))
        print("  those are the original line numbers, in the order they now print. "
              "Every line still prints: a line the order did not name kept its own "
              "place at the end.")
    if HIDDEN:
        print("  left off the page by name: %s"
              % ", ".join("%s (%d skills)" % (n, c) for n, c in HIDDEN))
        print("  that count above is the parse. These were removed after it, because "
              "you asked for them by heading.")
    unknown = OPTS["hide"] - set(n.strip().lower() for n, _c in HIDDEN)
    if unknown:
        sys.stderr.write("--hide-groups named %s, and no skills group has that "
                         "heading. Nothing was hidden for it.\n"
                         % ", ".join(sorted(unknown)))
    if OPTS["order"]:
        named = {slug(t.partition(":")[0]) for t in OPTS["order"]}
        extra = [s2["title"] for s2 in doc["sections"]
                 if s2["title"] and slug(s2["title"]) not in named]
        if extra:
            print("  --order did not name %s, so %s printed last in the main column. "
                  "Sections are never dropped here: to take one off the page, take it "
                  "out of the markdown." % (", ".join(extra),
                                            "they" if len(extra) > 1 else "it"))
    print("  %d sections, %d roles, %d bullets" % (len(doc["sections"]), roles, bullets))
    print("  skin: %s / %s / %s" % (skins["layouts"][a.layout]["label"],
                                    skins["palettes"][a.palette]["label"],
                                    skins["typesets"][a.typeset]["label"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
