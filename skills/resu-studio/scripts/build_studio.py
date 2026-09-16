"""Build the studio for one person, from their CV.

    python3 scripts/build_studio.py --cv "cv-<variant>.md" \\
        --role "Reporting and Insights Manager" \\
        [--letter "cover-letter-<variant>.md"] [--asks asks.json]

The studio is a template. It mentions nobody until this runs. Every line of the CV
block comes out of the markdown through the same parser the renderer uses, so the
studio and the printed page cannot drift: if the preview is not a promise about the
print, it is decoration.

Where it goes: the person's own documents folder, beside their finished PDFs, and
never inside the skill. See `paths.py` for why.

One studio at a time. Building a second one for a different advertisement keeps the
first, renamed with the date, because a studio somebody has spent an evening marking
up is not a file to overwrite quietly. Presenting several applications together in one
window is not built; this makes one, well.
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
TEMPLATE = os.path.join(ROOT, "assets", "studio.html")

sys.path.insert(0, HERE)
import render_cv as R          # noqa: E402  the parser the renderer already uses
import paths                   # noqa: E402
import documents               # noqa: E402


# ------------------------------------------------------------------ the person

def _lead_bold(text):
    """A line that opens in bold, split into its label and the rest.

    Education is usually written `**The degree**, the institution, the year`. The
    studio draws label and remainder differently and does not read markdown, so
    leaving the asterisks in prints them, literally, on somebody's CV.
    """
    m = re.match(r"^\s*\*\*(.+?)\*\*\s*[,.:-]?\s*(.*)$", text, re.S)
    if m:
        return {"lab": m.group(1).strip(), "txt": m.group(2).strip()}
    return {"lab": "", "txt": re.sub(r"\*\*(.+?)\*\*", r"\1", text).strip()}


ACHIEVEMENT_TITLES = ("key achievement", "achievement", "career highlight",
                      "selected achievement", "highlights")

#: What each section's line ids start with when the CV has no such heading. The
#: renderer builds every id from the heading it actually finds, so these are only
#: the fallbacks for a section that is not in this person's markdown at all.
DEFAULT_SID = {"profile": "profile", "skills": "key-skills",
               "experience": "professional-experience", "education": "education",
               "training": "training-certifications"}

BLOCK_NAME = {"para": "paragraph", "item": "bullet line",
              "labelled": "labelled line", "role": "role"}


def _unheld(section_title, blocks, dropped):
    """Name the blocks of a recognised section the studio has nowhere to put.

    A whole unrecognised section was always reported. Content inside a section the
    studio does know was not, so a profile written as bullets, or an intro paragraph
    above the roles, left the markdown, missed the studio and still printed from the
    renderer. Nothing may leave the page without being named.
    """
    if dropped is None or not blocks:
        return
    counts = {}
    for b in blocks:
        k = BLOCK_NAME.get(b["kind"], b["kind"])
        counts[k] = counts.get(k, 0) + 1
    for kind in sorted(counts):
        n = counts[kind]
        dropped.append("%d %s%s inside %s"
                       % (n, kind, "" if n == 1 else "s", section_title.strip()))


def cv_block(doc, dropped=None, achievements=None):
    """The CV as the studio wants it, built from the parsed markdown.

    Anything this does not recognise used to fall on the floor without a word. A CV
    with a `## Key Achievements` section opened in a studio that had no such section,
    which reads to the person as the work never having been done. Unrecognised
    sections, and now any block inside a recognised one that the studio cannot hold,
    are collected in `dropped` and named on the way past.

    `sid` carries the prefix each section's line ids are built from, taken from the
    heading with the renderer's own slug. The studio used to hold constants for these,
    so a CV headed `## TRAINING AND CERTIFICATIONS` marked lines the renderer had
    never heard of and every decision on them was dropped in silence.
    """
    out = {"name": doc["name"], "contact": doc["contact"], "profile": [],
           "skills": [], "roles": [], "education": [], "training": [],
           "sid": dict(DEFAULT_SID), "head": {}}
    for sec in doc["sections"]:
        title = (sec["title"] or "").strip().lower()
        blocks = sec["blocks"]
        left = []
        # The skills test comes first and is the renderer's own: any heading with the
        # word skill in it. `render_cv.is_skills` decides it that way for every section
        # before anything else is considered, so deciding it here in any other order
        # would put a heading in one section on this page and another in the print.
        if "skill" in title:
            out["sid"]["skills"] = R.slug(sec["title"]) or DEFAULT_SID["skills"]
            out["head"]["skills"] = (sec["title"] or "").strip()
            for b in blocks:
                if b["kind"] == "labelled":
                    label, text = b["label"], b["text"]
                elif b["kind"] in ("item", "para"):
                    # A plain line in a skills section is a group of its own with no
                    # heading, which is what the renderer makes of it: it carries an id
                    # of key-skills/group-N and prints. Leaving it out here made that
                    # line addressable in the print and nowhere on this page.
                    label, text = "", b["text"]
                else:
                    left.append(b)
                    continue
                items = []
                for it in R.split_items(text):
                    entry = {"n": it["name"]}
                    if it["level"]:
                        entry["l"] = it["level"]
                    if it["extra"]:
                        entry["y"] = it["extra"]
                    items.append(entry)
                out["skills"].append({"g": label, "items": items})
            _unheld(sec["title"], left, dropped)
            continue
        if any(t in title for t in ACHIEVEMENT_TITLES):
            # already on their CV, so it is ticked: the panel is where it is edited
            for b in blocks:
                if b["kind"] in ("item", "para") and (b.get("text") or "").strip():
                    achievements.append(b["text"].strip())
                elif b["kind"] == "labelled":
                    achievements.append("%s: %s" % (b["label"], b["text"]))
                else:
                    left.append(b)
            _unheld(sec["title"], left, dropped)
            continue
        if title.startswith("profile"):
            out["sid"]["profile"] = R.slug(sec["title"]) or DEFAULT_SID["profile"]
            out["head"]["profile"] = (sec["title"] or "").strip()
            for b in blocks:
                if b["kind"] == "para":
                    out["profile"].append(b["text"])
                else:
                    left.append(b)
        elif "experience" in title or "employment" in title:
            out["sid"]["experience"] = R.slug(sec["title"]) or DEFAULT_SID["experience"]
            out["head"]["experience"] = (sec["title"] or "").strip()
            for b in blocks:
                if b["kind"] == "role":
                    out["roles"].append({"t": b["title"], "d": b["dates"],
                                         "s": b.get("scope", []),
                                         "b": b.get("bullets", [])})
                else:
                    left.append(b)
        elif title.startswith("education"):
            out["sid"]["education"] = R.slug(sec["title"]) or DEFAULT_SID["education"]
            out["head"]["education"] = (sec["title"] or "").strip()
            for b in blocks:
                if b["kind"] == "labelled":
                    out["education"].append({"lab": b["label"], "txt": b["text"]})
                elif b["kind"] in ("para", "item"):
                    out["education"].append(_lead_bold(b["text"]))
                else:
                    left.append(b)
        elif "training" in title or "certification" in title:
            out["sid"]["training"] = R.slug(sec["title"]) or DEFAULT_SID["training"]
            out["head"]["training"] = (sec["title"] or "").strip()
            for b in blocks:
                if b["kind"] in ("item", "para"):
                    out["training"].append(b["text"])
                elif b["kind"] == "labelled":
                    out["training"].append("%s: %s" % (b["label"], b["text"]))
                else:
                    left.append(b)
        elif dropped is not None:
            if title:
                dropped.append(sec["title"].strip())
            else:
                # content above the first heading. The renderer prints it under a
                # section of its own, so it cannot go unmentioned here either.
                _unheld("the top of the file, above the first heading",
                        blocks, dropped)
            continue
        _unheld(sec["title"], left, dropped)
    return out


def letter_block(path, doc):
    """The cover letter as the studio wants it, or None."""
    if not path or not os.path.isfile(path):
        return None
    L = R.parse_letter(io.open(path, encoding="utf-8").read(), doc)
    to = list(L.get("to") or [])
    ref = ""
    for line in list(to):
        if re.match(r"^\s*(ref|reference|position number|vacancy)\b", line, re.I):
            ref = line
            to.remove(line)
    # `ph` is empty and `src` says file: a letter somebody wrote has no prompts in
    # it, and the studio needs to know this one came from a file so that a rebuild
    # carrying it can offer it rather than write over a letter typed in the browser.
    return {"date": L.get("date", ""), "to": to, "ref": ref,
            "re": L.get("re", ""), "sal": L.get("sal", ""),
            "paras": L.get("paras") or [],
            "close": L.get("close", ""), "sign": L.get("sign", ""),
            "ph": {}, "src": "file"}


# ---------------------------------------------------------------- the swap

def _const_span(text, name):
    """Where one top-level `const NAME = ...;` starts and ends.

    Bounded by the next top-level const rather than by counting brackets: the blocks
    contain braces inside strings and a counter gets them wrong.
    """
    i = text.find("const %s = " % name)
    if i < 0:
        raise SystemExit("the template has no `const %s`" % name)
    m = re.search(r"\nconst [A-Z_]+\s*=", text[i + 10:])
    if not m:
        raise SystemExit("could not find the end of `const %s`" % name)
    return i, i + 10 + m.start()


def swap_const(text, name, value):
    """Replace one top-level `const NAME = ...;` with new JSON."""
    i, j = _const_span(text, name)
    return (text[:i] + "const %s = " % name
            + json.dumps(value, ensure_ascii=False, separators=(",", ":")) + ";"
            + text[j:])


def swap_source(text, name, code):
    """Replace one top-level const with a JavaScript file, as a string literal.

    The studio injects paginate.js and markup.js into the sheet as text, so each one
    lived in the template as a second copy of a file that is also on disk. Two copies
    drift, and the one that drifted was the paginator: the sheet broke its pages in
    one place and the print broke them in another. The files are read at build time
    now, so there is one of each.
    """
    i, j = _const_span(text, name)
    lit = json.dumps(code, ensure_ascii=False).replace("</", "<\\/")
    return text[:i] + "const %s = " % name + lit + ";" + text[j:]


def _asset_text(name):
    path = os.path.join(ROOT, "assets", name)
    if not os.path.isfile(path):
        return None
    return io.open(path, encoding="utf-8").read()


def font_faces():
    """The bundled typefaces as @font-face rules, base64, one entry per face.

    The same files the print embeds, read the same way: `render_cv._font_files` finds
    them and `render_cv._family_name` names them, so a face is spelled identically in
    the studio and in the PDF. A studio that fetched its faces from a font server
    measured its page breaks in whatever the browser substituted whenever the network
    was slow, and then printed from different metrics. A face with no file bundled is
    simply absent here, and the page asks the font server for that one.
    """
    faces, missing = {}, []
    try:
        fonts, _sizes = R._fonts()
    except Exception:
        return {}, []
    for key in sorted(fonts):
        f = fonts[key]
        try:
            files = R._font_files(key)
        except Exception:
            files = []
        if not files:
            if f.get("g"):
                missing.append(key)
            continue
        name = R._family_name(f)
        css = []
        for weight, path in files:
            with open(path, "rb") as fh:
                blob = base64.b64encode(fh.read()).decode("ascii")
            ext = path.rsplit(".", 1)[-1].lower()
            css.append("@font-face{font-family:'%s';font-style:normal;font-weight:%s;"
                       "font-display:block;src:url(data:%s;base64,%s) format('%s')}"
                       % (name, weight, R._MIME.get(ext, "font/woff2"), blob,
                          "truetype" if ext in ("ttf", "otf") else ext))
        faces[key] = "".join(css)
    return faces, missing


def regroup_map():
    """assets/regroup.json's discipline map, as the renderer reads it.

    The studio shipped an empty map, so its By discipline chip regrouped nothing at
    all. Reading the same file the renderer reads is the only way the chip can show
    what --group discipline would print.
    """
    out = {}
    try:
        items = R._regroup_map() or []
    except Exception:
        return {}
    for label, srcs in items:
        names = [str(x) for x in (srcs or []) if str(x).strip()]
        if names:
            out[label] = names
    return out


def cv_ids(cv, letter=None):
    """Every line id this studio can address, which is every id the renderer builds.

    Used to check a proposal's `Line:` against something real. A `Line:` that matches
    nothing was loaded, counted and drawn against an empty stub, and its Use this
    wrote a mark keyed to an id the renderer would never meet.
    """
    sid = cv.get("sid") or DEFAULT_SID
    ids = {"name/0"}
    for i, _c in enumerate(cv.get("contact") or []):
        ids.add("contact/%d" % i)
    for i, _p in enumerate(cv.get("profile") or []):
        ids.add("%s/%d" % (sid["profile"], i))
    seen = {}
    for n, g in enumerate(cv.get("skills") or []):
        # the renderer's own numbering for two groups under the same heading
        sl = R.slug(g["g"])
        if not sl:
            ids.add("key-skills/group-%d" % (n + 1))
            continue
        seen[sl] = seen.get(sl, 0) + 1
        ids.add("key-skills/%s" % sl if seen[sl] == 1
                else "key-skills/%s-%d" % (sl, seen[sl]))
    for i, r in enumerate(cv.get("roles") or []):
        base = "%s/%d" % (sid["experience"], i)
        ids.add(base + "/h")
        ids.add(base + "/d")
        for j, _x in enumerate(r.get("s") or []):
            ids.add("%s/s%d" % (base, j))
        for j, _x in enumerate(r.get("b") or []):
            ids.add("%s/b%d" % (base, j))
    for i, _e in enumerate(cv.get("education") or []):
        ids.add("%s/%d" % (sid["education"], i))
    for i, _t in enumerate(cv.get("training") or []):
        ids.add("%s/%d" % (sid["training"], i))
    if letter:
        ids.update({"cover-letter/date", "cover-letter/ref", "cover-letter/re",
                    "cover-letter/sal", "cover-letter/close", "cover-letter/sign"})
        for i, _x in enumerate(letter.get("to") or []):
            ids.add("cover-letter/to%d" % i)
        for i, _x in enumerate(letter.get("paras") or []):
            ids.add("cover-letter/p%d" % i)
    return ids


def _norm(text):
    """One spelling for a line whose whitespace has moved.

    Markdown gets rewrapped: the same sentence broken over two lines instead of three
    is the same sentence, and a rebuild that called it a change would reset somebody
    for nothing.
    """
    return re.sub(r"\s+", " ", u"%s" % (text if text is not None else "")).strip()


def fingerprint(cv, letter=None):
    """A short, stable digest of the CV content this studio was built from.

    Every line id on the page is positional. `professional-experience/0/b3` means the
    fourth bullet of the first role and nothing else, so once a removal or a reorder is
    baked into the markdown the fourth bullet is a different sentence and every mark
    saved against that id lands somewhere it was never meant to. The studio cannot see
    that on its own: the state it reads out of the browser looks exactly the same
    either way. So the build stamps the CV's own fingerprint into the page and the
    studio saves the one it was working against. When the two differ, nothing keyed to
    a position is trusted until it has been checked against the wording it was made
    about.

    What goes in: everything a line id is built from or points at. The name and contact
    lines, the section id prefixes (they come from the headings, so renaming a heading
    renames every id under it), the profile paragraphs, every skills group with its
    items, every role with its dates, scope and bullets, education, training, and the
    cover letter, which has addressable lines of its own.

    What stays out, on purpose: the advertisement, the scorecard, the proposals and the
    drafted achievements, because state about those is keyed to an ask id or a proposal
    id and does not move when a bullet does; and every presentation choice there is,
    layout, palette, typeface, the regrouping map, the font files, the build date, the
    plugin version, the filenames, the role and the employer. Rebuilding to pick up a
    new skin, a rescored advertisement or a fresh set of proposals must reset nobody.
    """
    sid = cv.get("sid") or DEFAULT_SID
    doc = {
        "name": _norm(cv.get("name")),
        "contact": [_norm(c) for c in cv.get("contact") or []],
        "sid": dict((k, sid[k]) for k in sid),
        "profile": [_norm(p) for p in cv.get("profile") or []],
        "skills": [[_norm(g.get("g")),
                    [[_norm(i.get("n")), _norm(i.get("l")), _norm(i.get("y"))]
                     for i in g.get("items") or []]]
                   for g in cv.get("skills") or []],
        "roles": [[_norm(r.get("t")), _norm(r.get("d")),
                   [_norm(x) for x in r.get("s") or []],
                   [_norm(x) for x in r.get("b") or []]]
                  for r in cv.get("roles") or []],
        "education": [[_norm(e.get("lab")), _norm(e.get("txt"))]
                      for e in cv.get("education") or []],
        "training": [_norm(t) for t in cv.get("training") or []],
        "letter": None if not letter else [
            _norm(letter.get("date")), [_norm(x) for x in letter.get("to") or []],
            _norm(letter.get("ref")), _norm(letter.get("re")),
            _norm(letter.get("sal")),
            [_norm(p) for p in letter.get("paras") or []],
            _norm(letter.get("close")), _norm(letter.get("sign"))],
    }
    blob = json.dumps(doc, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:12]


def slug(text):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-",
                                     (text or "").lower())).strip("-") or "application"


def safe_filename(text):
    text = re.sub(r'[\\/:*?"<>|,;]+', " ", text or "Studio")
    return re.sub(r"\s+", " ", text).strip()[:70] or "Studio"


def studio_filename(a, doc):
    """<Role> - <Employer> - Studio.html, the way the PDFs are named.

    The employer is in the name for the same reason `render_cv._pdf_names` puts it
    in the PDF's: two applications for the same job title, built from the same
    markdown, otherwise produce one filename, and `documents.protect` sees the same
    role and the same source and lets the second write over the first. An evening of
    marking up goes, and nothing on screen says so. A segment with nothing in it is
    left out rather than printed as an empty gap between two hyphens.
    """
    bits = [safe_filename(a.role or doc["name"])]
    if (a.employer or "").strip():
        bits.append(safe_filename(a.employer))
    return " - ".join(b for b in bits if b) + " - Studio.html"


ID_RE = re.compile(r"^([A-Za-z][\w-]*)\b\s*(.*)$")


#: A field name inside a fenced block. Two words are allowed, because
#: `references/achievements.md` shows the field as `draws on` and the template shows
#: it as `draws_on`, and a person copying either one is writing the same field.
_KEY = r"([A-Za-z][\w]*(?: [A-Za-z][\w]*)?)"
_KEY_RE = re.compile(r"^%s:\s*(.*)$" % _KEY)
_SUBKEY_RE = re.compile(r"^\s+-?\s*%s:\s*(.*)$" % _KEY)


def _field_name(raw):
    """One spelling for a field written either way.

    `draws on` and `draws_on` are the same field, so a space is read as an
    underscore and everything downstream asks for one name. `draws_on:` stays the
    spelling the template shows.
    """
    return raw.strip().replace(" ", "_")


def _blocks(path):
    """The fenced `id: ...` records in asks.md and facts.md, as dicts.

    Keys are normalised: a field written `draws on:` is stored as `draws_on`, so a
    reader asks for one name and gets it whichever way the person wrote it.
    """
    if not path or not os.path.isfile(path):
        return {}
    out, cur, key = {}, None, None
    for raw in io.open(path, encoding="utf-8").read().split("\n"):
        line = raw.rstrip()
        if line.strip().startswith("```"):
            if cur and cur.get("id"):
                out[cur["id"]] = cur
            cur = {} if cur is None else None
            key = None
            continue
        if cur is None:
            continue
        m = _KEY_RE.match(line)
        if m:
            key = _field_name(m.group(1))
            cur[key] = m.group(2).strip().strip('"')
            continue
        m = _SUBKEY_RE.match(line)
        if m:
            # nested source lines: keep the first text/section we meet
            k, v = _field_name(m.group(1)), m.group(2).strip().strip('"')
            if k in ("text", "section", "cv") and k not in cur:
                cur[k] = v
    if cur and cur.get("id"):
        out[cur["id"]] = cur
    return out


STATE_WORDS = ("page", "buried", "off", "near", "missing", "none", "unscored")
# the old vocabulary, so a scorecard written before this template still opens
STATE_ALIAS = {"have": "page", "under another name": "buried", "partial": "near",
               "do not have": "missing", "not yet worked out": "unscored",
               "not checked yet": "unscored", "not a cv question": "none",
               "left off": "off", "on your cv": "page"}
ROWKIND = {"page": "met", "buried": "buried", "off": "off",
           "near": "near", "missing": "missing"}

#: All five words templates/scorecard.md allows for necessity. `condition` and
#: `not a cv question` used to be folded into `implied` on the way in, which showed a
#: citizenship or licence condition as a soft item lifted off the role description.
NECESSITY_WORDS = ("must", "nice", "implied", "condition", "not a cv question")


def scorecard_depth(path):
    """How deep the scorecard says it was scored, out of its frontmatter, or None."""
    if not path or not os.path.isfile(path):
        return None
    text = io.open(path, encoding="utf-8").read()
    m = re.match(r"^﻿?---\s*\n(.*?)\n---\s*(\n|$)", text, re.S)
    if not m:
        return None
    for line in m.group(1).split("\n"):
        hit = re.match(r"^\s*depth:\s*(.+?)\s*$", line)
        if hit:
            return hit.group(1).strip().strip('"').strip("'") or None
    return None


def score_rows(path):
    """The five-cell table out of scorecard.md, one dict per row."""
    if not path or not os.path.isfile(path):
        return []
    rows = []
    for raw in io.open(path, encoding="utf-8").read().split("\n"):
        line = raw.strip()
        if not line.startswith("|") or set(line) <= set("|- :"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) != 5:
            continue
        state = STATE_ALIAS.get(cells[2].lower(), cells[2].lower())
        if state not in STATE_WORDS:
            continue                      # the header row, and anything malformed
        rows.append({"ask": cells[0], "nec": cells[1].lower(),
                     "state": state, "ev": cells[3], "note": cells[4]})
    return rows


def asks_block(scorecard, asks_md, facts_md):
    """What the studio's Score tab draws.

    Three files it already has: the advertisement's own wording from `asks.md`, how
    the person sits against it from `scorecard.md`, and the verbatim line that
    answers it from `facts.md`. No fourth file, and no second opinion about the
    state — the scorecard says it and the studio shows it.
    """
    rows = score_rows(scorecard)
    if not rows:
        return []
    ads, facts = _blocks(asks_md), _blocks(facts_md)
    out = []
    for r in rows:
        # The first word is only an id when asks.md actually holds one by that name.
        # Treating it as an id regardless ate the first word of every row written
        # without one, so `SQL across large datasets` became the ask `across large
        # datasets` and nobody could see where the SQL had gone.
        m = ID_RE.match(r["ask"])
        if m and m.group(1) in ads:
            aid, rest = m.group(1), m.group(2).strip()
        else:
            aid, rest = (m.group(1) if m else r["ask"][:12]), r["ask"].strip()
        ad = ads.get(aid, {})
        text = ad.get("text") or rest or r["ask"]
        a = {"id": aid, "t": text,
             "n": r["nec"] if r["nec"] in NECESSITY_WORDS else "implied",
             "w": ad.get("where", ""), "st": r["state"], "r": []}
        if r["state"] == "unscored":
            a["u"] = True
        if r["state"] in ("none", "unscored"):
            out.append(a)
            continue

        kind = ROWKIND.get(r["state"], "near")
        ids = [x.strip() for x in r["ev"].replace(";", ",").split(",") if x.strip()]
        quoted = [(facts[i].get("text", ""), facts[i].get("section", ""))
                  for i in ids if i in facts and facts[i].get("text")]
        if quoted and r["state"] in ("page", "buried"):
            for text_, where_ in quoted:
                a["r"].append({"s": kind, "v": text_, "w": where_ or "your CV",
                               "n": r["note"]})
        elif quoted:
            # the record has it; this CV does not carry it on a line
            for text_, where_ in quoted:
                a["r"].append({"s": kind, "c": text_, "n": r["note"]})
        else:
            a["r"].append({"s": kind, "c": ", ".join(ids) or "nothing recorded yet",
                           "n": r["note"]})
        out.append(a)
    return out


PROP_RE = re.compile(r"^##\s+(P\d+)[.:]?\s*(.*)$")


def proposals_block(path, known=None):
    """proposals.md to what the studio's review queue needs.

    Keyed by the line id the change lands on, because the studio decides about
    lines and not about list items. A proposal with no `Line:` cannot be shown
    against anything on the page, so it is left out and named on the way past
    rather than silently dropped.

    A `Line:` that names an id this CV does not have is the same failure wearing a
    disguise, and it used to pass: it was loaded, counted in the total, drawn against
    an empty stub, and Use this wrote a mark against an id the renderer would never
    meet. It is checked against the ids the CV actually produced and reported by id.

    An entry with a `Line:` and no `Suggested:` is not malformed. `rewriting.md` says
    that where the stronger line needs a fact nobody has, the correct output is the
    question and not the rewrite, and the skill duly produces entries with nothing
    suggested. Those used to be dropped on the same path as an entry with no `Line:`,
    so the question never reached the person and the fact was never asked for. They
    are carried into the studio as a question against their line, with `kind: "ask"`
    and the question itself in `q`, taken from `Question:` where the entry has one and
    from `Why:` where it does not.
    """
    if not path or not os.path.isfile(path):
        return {}, [], []
    text = io.open(path, encoding="utf-8").read()
    out, skipped, unmatched, cur = {}, [], [], None

    def flush(c):
        if not c:
            return
        if not c.get("line"):
            skipped.append(c["p"])
            return
        if known is not None:
            # an addition sits after a line, so `<id>/+0` is real when `<id>` is
            base = c["line"].split("/+")[0]
            if c["line"] not in known and base not in known:
                unmatched.append("%s (%s)" % (c["p"], c["line"]))
                return
        cur_txt = (c.get("cur") or "").strip()
        sug = (c.get("sug") or "").strip()
        why = (c.get("why") or "").strip()
        question = (c.get("ask") or "").strip()
        kind = "edit"
        if cur_txt.lower().startswith("not on the cv"):
            kind = "add"
        if sug.lower().startswith("delete this"):
            kind = "remove"
        if kind != "remove" and not sug:
            # nothing to propose, because the wording waits on a fact only they have
            kind = "ask"
            question = question or why
            if not question:
                skipped.append(c["p"])
                return
        rec = {"p": c["p"], "kind": kind, "cur": cur_txt, "sug": sug,
               "where": c.get("where", ""), "why": why,
               "answers": c.get("answers", ""), "draws": c.get("draws", ""),
               "costs": c.get("costs", "")}
        if kind == "ask":
            rec["q"] = question
        out.setdefault(c["line"], []).append(rec)

    field, buf = None, []

    def stash():
        if cur is not None and field:
            cur[field] = " ".join(x.strip() for x in buf if x.strip())

    for raw in text.split("\n"):
        m = PROP_RE.match(raw.strip())
        if m:
            stash()
            flush(cur)
            cur = {"p": m.group(1), "where": m.group(2).strip()}
            field, buf = None, []
            continue
        if cur is None:
            continue
        low = raw.strip().lower()
        hit = None
        for key, name in (("**currently:**", "cur"), ("**suggested:**", "sug"),
                          ("**question:**", "ask"),
                          ("**why:**", "why"), ("**answers:**", "answers"),
                          ("**draws on:**", "draws"), ("**draws_on:**", "draws"),
                          ("**costs:**", "costs"),
                          ("**line:**", "line"), ("**decision:**", None)):
            if low.startswith(key):
                hit = (name, raw.strip()[len(key):].strip())
                break
        if hit:
            stash()
            field, buf = hit[0], ([hit[1]] if hit[1] else [])
            continue
        if field:
            buf.append(raw)
    stash()
    flush(cur)
    return out, skipped, unmatched


def achievements_block(path):
    """The drafted key achievements, for the studio's own Key achievements panel.

    The panel has always promised "six lines drawn out of your own record" and the
    template has always shipped an empty DRAFTS, so nothing could ever put a line
    there. Drafting them into `proposals.md` instead does not reach it: proposals sit
    on lines that already exist, and this section does not exist until somebody ticks
    something in it.
    """
    if not path or not os.path.isfile(path):
        return {}
    out = []
    for rec in _blocks(path).values():
        text = (rec.get("text") or "").strip()
        if not text:
            continue
        # `draws on` and `draws_on` are one field by the time _blocks has read it,
        # so a person who copied the spelling out of references/achievements.md and
        # a person who copied the template both land here.
        roles = [x.strip() for x in (rec.get("draws_on") or "").split(",")
                 if x.strip()]
        out.append({"id": rec.get("id", "k%d" % (len(out) + 1)), "t": text,
                    "w": (rec.get("answers") or "").strip() or "no ask named",
                    "roles": roles, "on": False})
    return {"achievements": out} if out else {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cv", required=True, help="the CV markdown for this application")
    ap.add_argument("--letter", default=None, help="the cover letter markdown")
    ap.add_argument("--asks", default=None, help="the scored advertisement, as JSON")
    ap.add_argument("--scorecard", default=None,
                    help="scorecard.md, which fills the studio's Score tab")
    ap.add_argument("--asks-md", dest="asks_md", default=None,
                    help="asks.md, for the advertisement's own wording")
    ap.add_argument("--facts", default=None,
                    help="facts.md, for the line that answers each ask")
    ap.add_argument("--achievements", default=None,
                    help="achievements.md, the drafted key achievements to pick from")
    ap.add_argument("--proposals", default=None,
                    help="proposals.md, so the suggestions are reviewed on the page")
    ap.add_argument("--role", default="",
                    help="the job title. Required: it names the file and keys this "
                         "application's own browser storage")
    ap.add_argument("--employer", default="", help="named in the header beside the role")
    ap.add_argument("--depth", default=None,
                    help="how deep the advertisement was scored, when scorecard.md "
                         "does not say so in its frontmatter")
    ap.add_argument("--out", default=None, help="where to write. Default: their documents folder")
    a = ap.parse_args()

    if not (a.role or "").strip():
        sys.stderr.write(
            "--role is required and was not given. It names the studio's file and keys "
            "this application's own browser storage, so without it every application "
            "for this person shares one store and a line marked in one shows up in "
            "another.\n")
        return 2

    if not os.path.isfile(a.cv):
        sys.stderr.write("no CV markdown at %s\n" % a.cv)
        return 2

    s = io.open(TEMPLATE, encoding="utf-8").read()
    doc = R.parse(io.open(a.cv, encoding="utf-8").read())
    if not doc["name"]:
        sys.stderr.write("that markdown has no `# Name` heading, so the studio would "
                         "open blank. Check the file.\n")
        return 2

    dropped, on_cv = [], []
    CV = cv_block(doc, dropped, on_cv)
    s = swap_const(s, "CV", CV)
    if dropped:
        sys.stderr.write(
            "this is in the markdown and the studio has nowhere to put it, so it is "
            "NOT on the page: %s. The studio knows a profile written as paragraphs, "
            "key skills written as `**Group:** item; item` lines, experience written "
            "as `### Role` blocks, education, training and key achievements. Fold the "
            "content into one of those or it does not print.\n" % ", ".join(dropped))
    asks = []
    if a.asks and os.path.isfile(a.asks):
        asks = json.load(io.open(a.asks, encoding="utf-8"))
    elif a.scorecard:
        asks = asks_block(a.scorecard, a.asks_md, a.facts)
        if not asks:
            sys.stderr.write(
                "that scorecard has no readable ask rows, so the Score tab would open "
                "empty. Every row needs all five cells and a state from the seven "
                "words in templates/scorecard.md.\n")
    s = swap_const(s, "ASKS", asks)

    # The letter and the drafted achievements are replaced too, not left as the
    # template found them. A studio that shows one application's letter under
    # another application's heading is wrong in the way nobody checks for.
    L = letter_block(a.letter, doc)
    if L:
        s = swap_const(s, "LETTER", L)
    drafted = achievements_block(a.achievements)
    # Lines already on their CV come first and arrive ticked, because they are already
    # printing. Anything drafted for this advertisement is offered underneath.
    if on_cv:
        # The id is taken from the wording and not from the position in the section.
        # Which of these lines a person has ticked is saved in the browser against this
        # id, and `m1` used to mean "the first key achievement on the CV" — so a
        # rebuild that added one at the top handed every tick to the line above it and
        # nothing said so. Keyed to the words, a tick can only ever come back to the
        # line it was made about, and a line whose wording changed loses its tick,
        # which is the right answer for a line that is no longer the same line.
        have = [{"id": "m" + hashlib.sha1(_norm(t).encode("utf-8")).hexdigest()[:10],
                 "t": t, "w": "already on your CV", "roles": [], "on": True}
                for t in on_cv]
        drafted["achievements"] = have + drafted.get("achievements", [])
    s = swap_const(s, "DRAFTS", drafted)
    if a.achievements and not drafted:
        sys.stderr.write("no readable achievements in %s, so that panel opens empty. "
                         "Each one needs a fenced block with id: and text:.\n"
                         % a.achievements)

    proposed, skipped, unmatched = proposals_block(a.proposals, cv_ids(CV, L))
    s = swap_const(s, "PROPOSED", proposed)
    if a.proposals:
        n = sum(len(v) for v in proposed.values())
        asked = sum(1 for v in proposed.values() for x in v if x["kind"] == "ask")
        print("%d suggestion%s loaded onto %d line%s%s"
              % (n, "" if n == 1 else "s", len(proposed),
                 "" if len(proposed) == 1 else "s",
                 "" if not asked
                 else ", %d of them a question rather than a rewrite" % asked))
        if skipped:
            sys.stderr.write(
                "these proposals have no `Line:`, or nothing at all to say about the "
                "line they name, so they cannot be shown against anything on the page "
                "and are not in the studio: %s. An entry with a `Line:` and no "
                "`Suggested:` is carried as a question, so it needs a `Question:` or a "
                "`Why:` for the person to answer.\n" % ", ".join(skipped))
        if unmatched:
            sys.stderr.write(
                "these proposals name a `Line:` that is not on this CV, so there is "
                "nothing on the page for them to change, and they are not in the "
                "studio: %s. The ids are built from the headings in the markdown, so "
                "check the id against the CV this studio was built from.\n"
                % ", ".join(unmatched))

    # The two scripts that run inside the sheet, read off disk. There is no second
    # copy of either in the template: see swap_source.
    for const, asset in (("PAGINATE", "paginate.js"), ("MARKUP", "markup.js")):
        code = _asset_text(asset)
        if code is None:
            sys.stderr.write(
                "assets/%s is missing, so the studio is built without it. The preview "
                "will not lay itself out on pages.\n" % asset)
            continue
        s = swap_source(s, const, code)

    # The typefaces, carried the way the print carries them.
    faces, no_file = font_faces()
    s = swap_const(s, "FONTFACE", faces)
    if no_file:
        sys.stderr.write(
            "no font file in assets/fonts for %s, so the studio fetches %s from the "
            "font server and measures in whatever the browser substitutes until it "
            "arrives. Run scripts/fetch_fonts.py to bundle them.\n"
            % (", ".join(no_file), "them" if len(no_file) > 1 else "it"))

    # The same regrouping the renderer would do for --group discipline.
    s = swap_const(s, "REGROUPMAP", regroup_map())

    # Which application this is, for the command the page copies out.
    s = swap_const(s, "ROLE", a.role)
    s = swap_const(s, "EMPLOYER", a.employer)

    # How deep the advertisement was scored. The studio used to assert that the person
    # had chosen this before the advertisement was read, which nothing recorded.
    depth = (a.depth or scorecard_depth(a.scorecard) or "unknown").strip()
    s = s.replace('const LEDGER={depth:"unknown"};',
                  'const LEDGER={depth:%s};' % json.dumps(depth, ensure_ascii=False), 1)

    # Which build made this page. A studio is a file on disk: updating the plugin
    # does not change one that already exists, so without a stamp there is no way to
    # tell a page built before a fix from one built after it.
    ver = "?"
    try:
        import json as _j
        _m = os.path.join(paths.SKILL, "..", "..", ".claude-plugin", "plugin.json")
        ver = _j.load(io.open(os.path.normpath(_m), encoding="utf-8")).get("version", "?")
    except Exception:
        pass
    s = s.replace("BUILD_STAMP", "Resu Studio %s &middot; this page built %s"
                  % (ver, datetime.date.today().isoformat()), 1)

    head = ". ".join(x for x in (a.role, a.employer) if x) or "This application"
    s = re.sub(r"<title>[^<]*</title>",
               "<title>Resu Studio - %s</title>" % (a.role or doc["name"]), s, count=1)
    s = s.replace("<p>No advertisement loaded yet.</p>", "<p>%s.</p>" % head, 1)

    # The handover names the files this studio was built from.
    s = s.replace('"CV - draft.md"', json.dumps(os.path.basename(a.cv)))
    s = s.replace('\\"CV - draft.md\\"', '\\"%s\\"' % os.path.basename(a.cv))
    if a.letter:
        s = s.replace('"Cover letter.md"', json.dumps(os.path.basename(a.letter)))
        s = s.replace('\\"Cover letter.md\\"', '\\"%s\\"' % os.path.basename(a.letter))

    # One browser store per application. Without this, marking a line in one
    # application shows up in another, which is the ghost every tool of this shape
    # grows when nobody keys the storage. The page holds the key in one const and
    # every read and write goes through it, including the copy the page keeps of the
    # state as it stood before a rebuilt CV was migrated, so that copy is inside this
    # application's own namespace too and the line printed below stays true.
    key = slug(". ".join(x for x in (a.role, a.employer) if x) or doc["name"])
    s = swap_const(s, "STORE", "cvwb:%s" % key)

    # What the saved marks are checked against. See `fingerprint`.
    fp = fingerprint(CV, L)
    s = swap_const(s, "FINGERPRINT", fp)

    out = a.out or os.path.join(paths.documents_dir(), studio_filename(a, doc))
    # `--out studio.html` gives a bare filename, whose dirname is "", and makedirs
    # of "" raises. Writing beside the working directory is what was asked for.
    if os.path.dirname(out):
        os.makedirs(os.path.dirname(out), exist_ok=True)
    # The employer travels into the ledger as well as into the name. Without it the
    # record cannot tell two employers hiring the same job title apart, which is the
    # commoner case and the one that costs somebody their work.
    kept = documents.protect(out, a.role, a.cv, employer=a.employer)
    io.open(out, "w", encoding="utf-8", newline="").write(s)
    documents.note(out, a.role, "studio", a.cv, employer=a.employer)

    print("wrote %s" % out)
    if kept:
        print("  kept the earlier studio as %s" % os.path.basename(kept))
    print("  person : %s, %d roles, %d skills groups, %d training lines"
          % (CV["name"], len(CV["roles"]), len(CV["skills"]), len(CV["training"])))
    print("  job    : %s" % head)
    print("  asks   : %d%s" % (len(asks), "" if asks else "   (not scored yet)"))
    print("  key ach: %d drafted%s"
          % (len(drafted.get("achievements", [])),
             "" if drafted else "   (none passed, that panel stays empty)"))
    print("  letter : %s" % ("loaded" if L else "none yet"))
    print("  store  : cvwb:%s, so this application cannot see any other" % key)
    print("  content: %s. Marks saved against a different one are checked against "
          "their own\n           wording before any of them is put back on a line."
          % fp)
    print()
    print("Hand the file over so they can open it themselves. It draws their own CV live")
    print("with every layout, palette and typeface as a control, and prints the command for")
    print("whatever they land on.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
