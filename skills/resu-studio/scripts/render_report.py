#!/usr/bin/env python3
"""Render scorecard.md to a self-contained HTML report with gauges.

    python3 render_report.py <scorecard.md> [--before <earlier-scorecard.md>]
                             [--palette forest] [--out FILE]

Two gauges, because there are two numbers and conflating them is the mistake this
whole workflow exists to avoid:

  what you have              measured against the facts ledger
  what a reader would find   measured against the page as it stands

The gap between them is the tailoring that has not happened yet.

Reads the scorecard and nothing else. Reports the numbers it finds; it does not
compute a score of its own, and it does not round.
"""

import argparse
import html
import json
import math
import os
import re
import sys

if os.name == "nt":
    # An agent reads this through a pipe, and a pipe on Windows uses the old code
    # page, so one accented letter would stop the script. See paths.utf8_output.
    for _stream in (sys.stdout, sys.stderr):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(os.path.dirname(HERE), "assets")

class Malformed(Exception):
    """Rows in the ask table that do not line up. Carries one line per fault."""


STATES = {
    # The studio's own words, so the printed report and the live Score tab describe
    # the same ask the same way. Two halves of one product using two vocabularies for
    # one idea is how somebody comes to believe they are looking at two findings.
    "page":     ("On your CV", "#2e7d52",
                 "A line on the CV above answers this, in wording close to theirs."),
    "buried":   ("On your CV, your wording", "#14607f",
                 "The work is on your CV. Their term for it is not, so a keyword "
                 "screen can miss it."),
    "off":      ("Left off this CV", "#a8681a",
                 "Your record answers this and this CV does not carry the line."),
    "near":     ("Half answered", "#7a6a3c",
                 "Part of the ask is answered and part is not. Nothing here claims "
                 "the rest."),
    "missing":  ("Nothing to say yet", "#a63b36",
                 "Nothing in your record touches this."),
    "none":     ("Not a CV question", "#5c6674",
                 "Handled outside the document, so no line is expected to answer it."),
    "unscored": ("Not checked yet", "#8b8b8b",
                 "In the advertisement, and nobody has set it against the record yet."),
}

#: Worst first. Somebody opening this wants the problems, not the confirmations.
STATE_ORDER = ["missing", "near", "off", "buried", "page", "none", "unscored"]

#: Older scorecards, and the words a person might reasonably write instead. Kept so a
#: scorecard written before the vocabulary settled still renders rather than refusing.
STATE_ALIASES = {
    "have": "page", "on your cv": "page",
    "under another name": "buried", "have, under another name": "buried",
    "on your cv, your wording": "buried", "another name": "buried",
    "left off this cv": "off", "off this cv": "off",
    "partial": "near", "half answered": "near",
    "do not have": "missing", "dont have": "missing", "don't have": "missing",
    "nothing to say yet": "missing",
    "not yet worked out": "unscored", "not checked yet": "unscored",
    "not yet checked": "unscored", "unchecked": "unscored",
    "not a cv question": "none", "condition of the job": "none",
}


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}, text
    d, key = {}, None
    for line in m.group(1).split("\n"):
        mm = re.match(r"^(\w[\w_]*):\s*(.*)$", line)
        if mm:
            key = mm.group(1)
            d[key] = mm.group(2).strip()
        else:
            mm = re.match(r"^\s+(\w[\w_]*):\s*(.*)$", line)
            if mm:
                d[mm.group(1)] = mm.group(2).strip()
    return d, text[m.end():]


# The two counts, in the studio's own vocabulary. Answered somewhere in the record
# is not the same as findable on the page, and `unscored` never counts toward either.
ANSWERED = ("page", "buried", "off")
ON_THE_PAGE = ("page",)

NECESSITIES = ("must", "nice", "implied", "condition", "not a cv question")


def counts_from_rows(rows):
    """The same coverage counts used by the Studio; partial is not complete."""
    return {"asks_total": len(rows), "must": sum(r["necessity"] == "must" for r in rows),
            "you_have": sum(r["state"] in ANSWERED for r in rows),
            "a_reader_would_find": sum(r["state"] in ON_THE_PAGE for r in rows),
            "unscored": sum(r["state"] == "unscored" for r in rows)}


def asks_table(text):
    """Read the ask rows, and refuse the moment a row does not line up.

    The columns are read by position, so one missing cell silently shifts every
    later cell one to the left: the state lands in the necessity column, the
    evidence lands in the state column, and the renderer, finding no state it
    recognises, draws a neutral grey pill and carries on. The report then shows a
    bar chart counting only the rows that happened to parse while the gauges above
    it count all of them, and nothing on the page says the two disagree.

    That is the exact failure this whole skill exists to refuse: a document that
    looks finished and is wrong in a way the person cannot see. So a malformed row
    is fatal here, and the message names the row so it can be fixed at the source.
    """
    rows, faults = [], []
    for n, line in enumerate(text.split("\n"), 1):
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells or cells[0].lower() in ("ask", "") or set(cells[0]) <= set("-: "):
            continue

        if len(cells) != 5:
            faults.append("line %d: %d columns, expected 5 (Ask, Necessity, State, "
                          "Evidence, Note). %r" % (n, len(cells), cells[0][:44]))
            continue
        nec, st = cells[1].lower(), cells[2].lower()
        st = STATE_ALIASES.get(st, st)
        if st not in STATES:
            hint = ""
            if nec in STATES:
                hint = (". The state %r is sitting in the Necessity column, so this "
                        "row is shifted one to the left" % nec)
            faults.append("line %d: %r is not a state%s. %r"
                          % (n, cells[2][:34], hint, cells[0][:44]))
            continue
        if nec not in NECESSITIES:
            faults.append("line %d: %r is not a necessity. Expected one of %s. %r"
                          % (n, cells[1][:26], ", ".join(NECESSITIES), cells[0][:44]))
            continue

        rows.append({"id": cells[0], "necessity": nec, "state": st,
                     "evidence": cells[3], "note": cells[4]})

    if faults:
        raise Malformed(faults)
    return rows


def gauge(value, total, label, sub, colour, before=None):
    """One gauge in its own card, the way the studio's Score tab draws it."""
    total = max(total, 1)
    frac = min(max(value / total, 0.0), 1.0)
    r, cx, cy = 62, 80, 80
    circ = math.pi * r
    arc = "M %d %d A %d %d 0 0 1 %d %d" % (cx - r, cy, r, r, cx + r, cy)
    marker = ""
    if before is not None:
        bfrac = min(max(before / total, 0.0), 1.0)
        ang = math.pi * (1 - bfrac)
        marker = ('<circle cx="%.1f" cy="%.1f" r="4.5" fill="#fff" stroke="#5c6674" '
                  'stroke-width="2"><title>was %d</title></circle>'
                  % (cx + r * math.cos(ang), cy - r * math.sin(ang), before))
    return ("""<div class="gcard">
<h3>%s</h3>
<svg viewBox="0 0 160 104" role="img" aria-label="%s of %s">
  <path d="%s" fill="none" stroke="#e4e7ec" stroke-width="13" stroke-linecap="round"/>
  <path d="%s" fill="none" stroke="%s" stroke-width="13" stroke-linecap="round"
        stroke-dasharray="%.2f %.2f"/>
  %s
</svg>
<p class="gnum">%d <span>of %d</span></p>
<p class="gsub">%s</p></div>"""
            % (html.escape(label), value, total, arc, arc, colour, circ * frac, circ,
               marker, value, total, html.escape(sub)))


def stack(rows):
    """One bar, every state in it, with the key on the same line as the colour."""
    counts = {}
    for r in rows:
        counts[r["state"]] = counts.get(r["state"], 0) + 1
    total = max(len(rows), 1)
    seg, key = [], []
    for k in STATE_ORDER:
        n = counts.get(k, 0)
        if not n:
            continue
        label, colour, _b = STATES[k]
        seg.append('<i style="width:%.3f%%;background:%s" title="%s: %d"></i>'
                   % (100.0 * n / total, colour, html.escape(label), n))
        key.append('<span><i style="background:%s"></i>%s <b>%d</b></span>'
                   % (colour, html.escape(label), n))
    return ('<div class="stack">%s</div>\n<div class="key">%s</div>'
            % ("".join(seg), "".join(key)))


def askrows(rows):
    """Each ask as its own row, worst first, the way the studio lists them."""
    order = {k: i for i, k in enumerate(STATE_ORDER)}
    nec = {"must": "Essential", "nice": "Desirable", "implied": "From the role description",
           "condition": "Condition", "not a cv question": "Condition"}
    out = ['<div class="asks">']
    for r in sorted(rows, key=lambda x: (order.get(x["state"], 99), x["id"])):
        label, colour, _b = STATES.get(r["state"], (r["state"], "#8b8b8b", ""))
        meta = nec.get(r["necessity"], r["necessity"].title())
        ident = r["id"].split(" ", 1)
        num = ident[0] if len(ident) > 1 else ""
        text = ident[1] if len(ident) > 1 else r["id"]
        bits = [meta]
        out.append(
            '<div class="ask"><i class="dot" style="background:%s"></i>'
            '<div class="at"><p class="t">%s%s</p><p class="m">%s</p>%s</div>'
            '<span class="tag" style="color:%s;border-color:%s">%s</span></div>'
            % (colour,
               ('<em>%s</em> ' % html.escape(num)) if num else "",
               html.escape(text),
               " &middot; ".join(bits),
               (('<p class="n">%s</p>' % html.escape(r["note"])) if r["note"] else "")
               + (('<p class="ev">%s</p>' % html.escape(r["evidence"]))
                  if r["evidence"] else ""),
               colour, colour, html.escape(label)))
    out.append("</div>")
    return "\n".join(out)


def prose(text):
    body = re.sub(r"\n#.*", "", text.split("\n|")[0])
    body = body.split("# Ask by ask")[0]
    out = []
    for para in re.split(r"\n\s*\n", body.strip()):
        p = para.strip()
        if not p or p.startswith("|") or p.startswith("#"):
            continue
        # A rule in markdown is a rule, not three hyphens printed on the page.
        if set(p) <= set("-*_ ") and len(p) >= 3:
            out.append('<hr class="rule">')
            continue
        p = html.escape(p).replace("\n", " ")
        p = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", p)
        out.append("<p>%s</p>" % p)
    return "\n".join(out)


CSS = """
*{box-sizing:border-box}
body{margin:0;background:#eef0f3;color:#12161c;
     font:15px/1.55 "Hanken Grotesk","Helvetica Neue",Arial,sans-serif}
.wrap{max-width:1060px;margin:26px auto 60px;background:#fff;padding:34px 40px 46px;
      box-shadow:0 2px 14px rgba(0,0,0,.10)}
h1{font-size:22px;margin:0 0 3px;letter-spacing:-.01em}
.meta{color:#5c6674;font-size:13px;margin:0 0 20px}
.verdict{display:inline-block;padding:5px 13px;border-radius:20px;color:#fff;
         font-weight:700;font-size:12.5px;letter-spacing:.3px}
h2{font-family:var(--label);font-size:11.5px;margin:30px 0 12px;letter-spacing:.13em;
   text-transform:uppercase;color:#5c6674;font-weight:700}

/* two gauges, in cards, as the Score tab draws them */
.gauges{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:20px 0 16px}
.gcard{background:#f6f7f9;border:1px solid #e4e7ec;border-radius:10px;
       padding:16px 18px 18px;text-align:center}
.gcard h3{font-family:var(--label);font-size:11px;letter-spacing:.13em;
          text-transform:uppercase;color:#5c6674;margin:0 0 6px;font-weight:700}
.gcard svg{width:150px;height:97px;display:block;margin:0 auto}
.gnum{font-size:25px;font-weight:700;margin:2px 0 4px}
.gnum span{font-size:14px;font-weight:400;color:#5c6674}
.gsub{color:#5c6674;font-size:12.5px;margin:0;line-height:1.4}

/* one stacked bar, and its key on the same colours */
.stack{display:flex;height:11px;border-radius:6px;overflow:hidden;background:#e4e7ec;
       margin:4px 0 9px}
.stack i{display:block;height:100%}
.key{display:flex;flex-wrap:wrap;gap:6px 18px;font-size:12.5px;color:#5c6674;
     margin:0 0 14px}
.key span{display:flex;align-items:center;gap:6px}
.key i{width:9px;height:9px;border-radius:2px;flex:none}
.key b{color:#12161c}

.gap{background:#fbf7ea;border-left:4px solid #a8681a;padding:12px 15px;
     margin:14px 0 22px;font-size:14px}

/* one row per ask, worst first */
.asks{border-top:1px solid #e4e7ec}
.ask{display:flex;gap:12px;align-items:flex-start;padding:11px 2px;
     border-bottom:1px solid #eceef1}
.dot{width:9px;height:9px;border-radius:50%;flex:none;margin-top:6px}
.at{flex:1;min-width:0}
.at .t{margin:0;font-size:14.5px;line-height:1.4}
.at .t em{color:#8b93a0;font-style:normal;font-size:12px;margin-right:2px}
.at .m{margin:2px 0 0;font-family:var(--label);font-size:10.5px;letter-spacing:.09em;
       text-transform:uppercase;color:#8b93a0}
.at .n{margin:5px 0 0;font-size:13px;color:#5c6674}
.at .ev{margin:3px 0 0;font-size:11.5px;color:#8b93a0;
        font-family:ui-monospace,Menlo,Consolas,monospace}
.tag{flex:none;font-family:var(--label);font-size:10px;letter-spacing:.09em;
     text-transform:uppercase;font-weight:700;border:1px solid;border-radius:4px;
     padding:3px 7px;white-space:nowrap;margin-top:2px}

p{margin:0 0 11px}
.legend{color:#5c6674;font-size:12.5px;margin-top:14px}
hr.rule{border:0;border-top:1px solid #e4e7ec;margin:18px 0}
:root{--label:"Archivo Narrow","Hanken Grotesk","Helvetica Neue",Arial,sans-serif}
@media (max-width:720px){.gauges{grid-template-columns:1fr}
  .ask{flex-wrap:wrap}.tag{margin-left:21px}}
@media print{body{background:#fff}.wrap{box-shadow:none;margin:0;max-width:none}
  .ask{break-inside:avoid}}
"""

VERDICT_COLOUR = {"strong": "#2e7d4f", "worth it": "#3f7d9e",
                  "a stretch": "#c2681d", "not this one": "#a33232"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scorecard")
    ap.add_argument("--before")
    ap.add_argument("--out")
    a = ap.parse_args()

    text = read(a.scorecard)
    fm, body = frontmatter(text)
    try:
        rows = asks_table(body)
    except Malformed as bad:
        sys.stderr.write(
            "REFUSING TO WRITE THE SCORECARD. %d row(s) in the ask table do not line "
            "up, and rendering them anyway produces a report whose bar chart and "
            "gauges disagree without saying so.\n" % len(bad.args[0]))
        for f in bad.args[0][:20]:
            sys.stderr.write("  %s\n" % f)
        if len(bad.args[0]) > 20:
            sys.stderr.write("  ... and %d more\n" % (len(bad.args[0]) - 20))
        sys.stderr.write(
            "  Every row needs all five cells, even when a cell is empty:\n"
            "    | a25 the ask | implied | partial | fact-id | note |\n"
            "  An ask with no necessity still needs the column, left blank as `implied`.\n")
        return 1

    def num(key, default=0):
        try:
            return int(re.sub(r"[^0-9]", "", fm.get(key, "")) or default)
        except ValueError:
            return default

    actual = counts_from_rows(rows) if rows else {k:num(k) for k in ("asks_total", "you_have", "a_reader_would_find")}
    total, have, find = actual["asks_total"], actual["you_have"], actual["a_reader_would_find"]

    b_have = b_find = None
    if a.before:
        bfm, bbody = frontmatter(read(a.before))
        try:
            brows = asks_table(bbody)
        except Malformed:
            sys.stderr.write("the earlier scorecard has malformed rows; "
                             "rendering without the before markers.\n")
            brows = []
        if brows:
            before_counts = counts_from_rows(brows)
            b_have, b_find = before_counts["you_have"], before_counts["a_reader_would_find"]

    verdict = fm.get("verdict", "").strip().lower()
    vcol = VERDICT_COLOUR.get(verdict, "#4b5563")

    gap = have - find
    gap_note = ("Every one of the %d asks you answer is already visible on the page."
                % have if gap <= 0 else
                "%d ask%s you answer %s not visible to a reader of the current page. "
                "That gap is what the rewrite closes." %
                (gap, "" if gap == 1 else "s", "is" if gap == 1 else "are"))

    parts = ['<div class="wrap">',
             "<h1>%s</h1>" % html.escape(fm.get("job", "You against it")),
             '<p class="meta">%s &nbsp;|&nbsp; %s &nbsp;|&nbsp; scored %s</p>'
             % (html.escape(fm.get("variant", "")), html.escape(fm.get("stage", "")),
                html.escape(fm.get("scored", "")))]
    if verdict:
        parts.append('<span class="verdict" style="background:%s">%s</span>'
                     % (vcol, html.escape(verdict)))
    parts.append('<div class="gauges">')
    parts.append(gauge(have, total, "What you have",
                       "measured against your history", "#2e7d4f", b_have))
    parts.append(gauge(find, total, "What a reader would find",
                       "measured against the page as it stands", "#3f7d9e", b_find))
    parts.append("</div>")
    if a.before:
        parts.append('<p class="legend">The hollow marker on each gauge is where this '
                     'stood before your decisions.</p>')
    parts.append('<div class="gap">%s</div>' % html.escape(gap_note))
    parts.append(prose(body))
    if rows:
        parts.append("<h2>How each ask sits</h2>")
        parts.append(stack(rows))
        parts.append(askrows(rows))
        parts.append('<p class="legend">&ldquo;Not checked yet&rdquo; is counted '
                     'apart from &ldquo;Nothing to say yet&rdquo;. One means nobody '
                     'has looked; the other means the answer is no. &ldquo;Not a CV '
                     'question&rdquo; is neither: it is handled outside the document, '
                     'so no line is expected to answer it.</p>')
    parts.append("</div>")

    out = a.out or os.path.splitext(a.scorecard)[0] + ".html"
    with open(out, "w", encoding="utf-8") as f:
        f.write("<!doctype html><html><head><meta charset=\"utf-8\"><title>%s</title>"
                "<style>%s</style></head><body>%s</body></html>"
                % (html.escape(fm.get("job", "Scorecard")), CSS, "\n".join(parts)))
    print("wrote %s" % out)
    print("  %d asks, %d you have, %d a reader would find" % (total, have, find))
    if rows:
        print("  %d rows in the ask table" % len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
