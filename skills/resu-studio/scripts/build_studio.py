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
import datetime
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


def cv_block(doc, dropped=None, achievements=None):
    """The CV as the studio wants it, built from the parsed markdown.

    Anything this does not recognise used to fall on the floor without a word. A CV
    with a `## Key Achievements` section opened in a studio that had no such section,
    which reads to the person as the work never having been done. Unrecognised
    sections are now collected in `dropped` and named on the way past.
    """
    out = {"name": doc["name"], "contact": doc["contact"], "profile": "",
           "skills": [], "roles": [], "education": [], "training": []}
    for sec in doc["sections"]:
        title = (sec["title"] or "").strip().lower()
        blocks = sec["blocks"]
        if any(t in title for t in ACHIEVEMENT_TITLES):
            # already on their CV, so it is ticked: the panel is where it is edited
            for b in blocks:
                if b["kind"] in ("item", "para") and (b.get("text") or "").strip():
                    achievements.append(b["text"].strip())
                elif b["kind"] == "labelled":
                    achievements.append("%s: %s" % (b["label"], b["text"]))
            continue
        if title.startswith("profile"):
            out["profile"] = " ".join(b["text"] for b in blocks if b["kind"] == "para")
        elif "skill" in title:
            for b in blocks:
                if b["kind"] != "labelled":
                    continue
                items = []
                for it in R.split_items(b["text"]):
                    entry = {"n": it["name"]}
                    if it["level"]:
                        entry["l"] = it["level"]
                    if it["extra"]:
                        entry["y"] = it["extra"]
                    items.append(entry)
                out["skills"].append({"g": b["label"], "items": items})
        elif "experience" in title or "employment" in title:
            for b in blocks:
                if b["kind"] == "role":
                    out["roles"].append({"t": b["title"], "d": b["dates"],
                                         "s": b.get("scope", []),
                                         "b": b.get("bullets", [])})
        elif title.startswith("education"):
            for b in blocks:
                if b["kind"] == "labelled":
                    out["education"].append({"lab": b["label"], "txt": b["text"]})
                elif b["kind"] in ("para", "item"):
                    out["education"].append(_lead_bold(b["text"]))
        elif "training" in title or "certification" in title:
            for b in blocks:
                if b["kind"] in ("item", "para"):
                    out["training"].append(b["text"])
                elif b["kind"] == "labelled":
                    out["training"].append("%s: %s" % (b["label"], b["text"]))
        elif title and dropped is not None:
            dropped.append(sec["title"].strip())
    return out


def letter_block(path, doc):
    """The cover letter as the studio wants it, or None."""
    if not path or not os.path.isfile(path):
        return None
    L = R.parse_letter(io.open(path, encoding="utf-8").read(), doc)
    to = list(L.get("to") or [])
    ref = ""
    for line in list(to):
        if re.match(r"^\s*(ref|reference|position number)\b", line, re.I):
            ref = line
            to.remove(line)
    return {"date": L.get("date", ""), "to": to, "ref": ref,
            "sal": L.get("sal", ""), "paras": L.get("paras") or [],
            "close": L.get("close", ""), "sign": L.get("sign", "")}


# ---------------------------------------------------------------- the swap

def swap_const(text, name, value):
    """Replace one top-level `const NAME = ...;` with new JSON.

    Bounded by the next top-level const rather than by counting brackets: the blocks
    contain braces inside strings and a counter gets them wrong.
    """
    i = text.find("const %s = " % name)
    if i < 0:
        raise SystemExit("the template has no `const %s`" % name)
    m = re.search(r"\nconst [A-Z_]+\s*=", text[i + 10:])
    if not m:
        raise SystemExit("could not find the end of `const %s`" % name)
    j = i + 10 + m.start()
    return (text[:i] + "const %s = " % name
            + json.dumps(value, ensure_ascii=False, separators=(",", ":")) + ";"
            + text[j:])


def slug(text):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-",
                                     (text or "").lower())).strip("-") or "application"


def safe_filename(text):
    text = re.sub(r'[\\/:*?"<>|,;]+', " ", text or "Studio")
    return re.sub(r"\s+", " ", text).strip()[:70] or "Studio"


ID_RE = re.compile(r"^([A-Za-z][\w-]*)\b\s*(.*)$")


def _blocks(path):
    """The fenced `id: ...` records in asks.md and facts.md, as dicts."""
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
        m = re.match(r"^(\w[\w_]*):\s*(.*)$", line)
        if m:
            key = m.group(1)
            cur[key] = m.group(2).strip().strip('"')
            continue
        m = re.match(r"^\s+-?\s*(\w[\w_]*):\s*(.*)$", line)
        if m:
            # nested source lines: keep the first text/section we meet
            k, v = m.group(1), m.group(2).strip().strip('"')
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
        m = ID_RE.match(r["ask"])
        aid = m.group(1) if m else r["ask"][:12]
        rest = (m.group(2).strip() if m else "")
        ad = ads.get(aid, {})
        text = ad.get("text") or rest or r["ask"]
        a = {"id": aid, "t": text,
             "n": r["nec"] if r["nec"] in ("must", "nice", "implied") else "implied",
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


def proposals_block(path):
    """proposals.md to what the studio's review queue needs.

    Keyed by the line id the change lands on, because the studio decides about
    lines and not about list items. A proposal with no `Line:` cannot be shown
    against anything on the page, so it is left out and named on the way past
    rather than silently dropped.
    """
    if not path or not os.path.isfile(path):
        return {}, []
    text = io.open(path, encoding="utf-8").read()
    out, skipped, cur = {}, [], None

    def flush(c):
        if not c:
            return
        if not c.get("line"):
            skipped.append(c["p"])
            return
        cur_txt = (c.get("cur") or "").strip()
        sug = (c.get("sug") or "").strip()
        kind = "edit"
        if cur_txt.lower().startswith("not on the cv"):
            kind = "add"
        if sug.lower().startswith("delete this"):
            kind = "remove"
        if kind != "remove" and not sug:
            skipped.append(c["p"])
            return
        out.setdefault(c["line"], []).append(
            {"p": c["p"], "kind": kind, "cur": cur_txt, "sug": sug,
             "where": c.get("where", ""), "why": (c.get("why") or "").strip(),
             "answers": c.get("answers", ""), "draws": c.get("draws", ""),
             "costs": c.get("costs", "")})

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
                          ("**why:**", "why"), ("**answers:**", "answers"),
                          ("**draws on:**", "draws"), ("**costs:**", "costs"),
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
    return out, skipped


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
        roles = [x.strip() for x in
                 (rec.get("draws on") or rec.get("draws_on") or "").split(",")
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
    ap.add_argument("--role", default="", help="the job title, for the filename and header")
    ap.add_argument("--employer", default="", help="named in the header beside the role")
    ap.add_argument("--out", default=None, help="where to write. Default: their documents folder")
    a = ap.parse_args()

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
            "these sections are in the markdown and the studio has nowhere to put "
            "them, so they are NOT on the page: %s. The studio knows profile, key "
            "skills, experience, education, training and key achievements. Fold the "
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
        have = [{"id": "m%d" % (i + 1), "t": t, "w": "already on your CV",
                 "roles": [], "on": True} for i, t in enumerate(on_cv)]
        drafted["achievements"] = have + drafted.get("achievements", [])
    s = swap_const(s, "DRAFTS", drafted)
    if a.achievements and not drafted:
        sys.stderr.write("no readable achievements in %s, so that panel opens empty. "
                         "Each one needs a fenced block with id: and text:.\n"
                         % a.achievements)

    proposed, skipped = proposals_block(a.proposals)
    s = swap_const(s, "PROPOSED", proposed)
    if a.proposals:
        n = sum(len(v) for v in proposed.values())
        print("%d suggestion%s loaded onto %d line%s"
              % (n, "" if n == 1 else "s", len(proposed),
                 "" if len(proposed) == 1 else "s"))
        if skipped:
            sys.stderr.write(
                "these proposals have no `Line:` so they cannot be shown against "
                "anything on the page, and are not in the studio: %s\n"
                % ", ".join(skipped))

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
    # grows when nobody keys the storage.
    key = slug(a.role or doc["name"])
    s = s.replace('localStorage.getItem("cvwb")', 'localStorage.getItem("cvwb:%s")' % key)
    s = s.replace('localStorage.setItem("cvwb"', 'localStorage.setItem("cvwb:%s"' % key)

    out = a.out or os.path.join(paths.documents_dir(),
                                "%s - Studio.html" % safe_filename(a.role or doc["name"]))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    kept = documents.protect(out, a.role, a.cv)
    io.open(out, "w", encoding="utf-8", newline="").write(s)
    documents.note(out, a.role, "studio", a.cv)

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
    print()
    print("Open it and hand them the link. It draws their own CV live with every")
    print("layout, palette and typeface as a control, and prints the command for")
    print("whatever they land on.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
