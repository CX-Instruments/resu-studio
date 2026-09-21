#!/usr/bin/env python3
"""Bake the decisions into the markdown, so the markdown is the document.

    python3 scripts/assemble.py <source cv markdown> --decisions <cv-decisions.json> \\
        --out <cv-variant.md> [--archive <cv-variant-archive.md>] [--variant <name>]

`cv-<variant>.md` is the deliverable and the master. That is only true if it holds
everything: the wording the person rewrote, the lines they took off actually gone,
the lines they added in the place they added them, every list in the order they put
it in, and every extra section they ticked written in as a real section. This script
is what makes it true.

It works on the raw lines rather than on a re-emitted parse tree, so anything nobody
decided anything about is copied through byte for byte: the headings, the blank
lines, the wrapping, the indentation and the person's own punctuation. Assembling
with an empty decisions file gives back the file it was handed, byte identical.

Three things come out of one run:

    the assembled markdown   everything in it, and a one line machine note at the
                             foot saying which decisions are already baked in
    the archive              every line taken off and every rewrite, in full, so
                             nothing is lost when a removal leaves the markdown
    a report                 what was baked, and what the decisions file asked for
                             that this CV has no line for

The note is what stops the same decisions being applied twice. `render_cv.py
--decisions` reads it: offered the decisions that are already in the file it applies
nothing and says so, and offered different ones it applies them normally, because a
person can mark up a studio built from the assembled CV and those decisions are
relative to the assembled document.

Standard library only.

    0   written
    1   refused, and the reason said
    2   the command line was wrong
"""

import argparse
import datetime
import json
import os
import re
import sys
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import render_cv as R                                          # noqa: E402

RULE = re.compile(r"^(-{3,}|\*{3,})$")
LABELLED = re.compile(r"^\*\*(.+?):\*\*\s*(.*)$")

# A continuation line that comes out looking like markup would be read back as a
# different line, so wrapping is abandoned when it would produce one of these.
LOOKS_LIKE_MARKUP = (
    lambda t: (not t or t.startswith("#") or t.startswith("- ") or t.startswith("* ")
               or bool(LABELLED.match(t)) or bool(RULE.match(t))
               or R._is_note_line(t)))


def _lead(s):
    return s[:len(s) - len(s.lstrip())]


def _flat(s):
    return " ".join((s or "").split())


# ------------------------------------------------------------------ scanning

def scan(md):
    """Every addressable line of a CV markdown, with the raw lines it sits on.

    The ids are `render_cv.py`'s own: the ones the studio marks against and the ones
    `--decisions` applies to. The branches below follow `render_cv.parse` step for
    step, and `verify()` proves the two agree by rendering both sides and comparing
    what comes out, so a drift between them is refused rather than printed.
    """
    lines = md.split("\n")
    n = len(lines)

    def bare(i):
        return lines[i].strip()

    def prose(start):
        buf, j = [], start
        while j < n:
            t = bare(j)
            if (not t or t.startswith("#") or t.startswith("- ") or t.startswith("* ")
                    or LABELLED.match(t) or RULE.match(t) or R._is_note_line(t)):
                break
            buf.append(t)
            j += 1
        return " ".join(buf), j

    def unit(uid, kind, text, start, end, **kw):
        u = {"id": uid, "kind": kind, "text": text, "start": start, "end": end,
             "lead": _lead(lines[start]), "label": "", "marker": "", "cont": None,
             "raw": lines[start:end], "wrapped": end - start > 1, "width": 0}
        if u["wrapped"]:
            # the indent this file gives a continuation line, even when that is none
            u["cont"] = _lead(lines[start + 1])
            u["width"] = max(len(x) for x in lines[start:end])
        u.update(kw)
        units.append(u)
        return u

    units, sections, notes = [], [], []
    floating = {"title": "", "sid": "section", "skills": False, "ri": 0, "flat": 0,
                "head": None, "roles": [], "flats": [], "groups": []}
    floating_used = False

    def owner_of(sec):
        nonlocal floating_used
        if sec is not None:
            return sec
        if not floating_used:
            floating_used = True
            sections.append(floating)
        return floating

    sec = role = None
    name_done = False
    i = 0
    while i < n:
        t = bare(i)
        if R._is_note_line(t):
            notes.append(i)
            i += 1
            continue
        if not t or RULE.match(t):
            i += 1
            continue

        if t.startswith("# ") and not name_done:
            name_done = True
            unit("name/0", "name", t[2:].strip(), i, i + 1, prefix="# ")
            i += 1
            continue

        if t.startswith("## "):
            title = t[3:].strip()
            sec = {"title": title, "sid": R.slug(title) or "section",
                   "skills": R.is_skills(title), "ri": 0, "flat": 0, "head": i,
                   "roles": [], "flats": [], "groups": []}
            sections.append(sec)
            role = None
            i += 1
            continue

        if t.startswith("### "):
            head = t[4:].strip()
            title, dates = head, ""
            if "|" in head:
                title, dates = [p.strip() for p in head.rsplit("|", 1)]
            start = i
            i += 1
            dspan = None
            if not dates:
                j = i
                while j < n and not bare(j):
                    j += 1
                if j < n and R._is_date_line(bare(j)):
                    dates = bare(j)
                    dspan = (j, j + 1)
                    i = j + 1
            own = owner_of(sec)
            base = "%s/%d" % (own["sid"], own["ri"])
            own["ri"] += 1
            role = {"base": base, "start": start, "end": i, "scope": [], "bullets": [],
                    "dates_in_head": dates and dspan is None, "title": title,
                    "dates": dates}
            own["roles"].append(role)
            role["head"] = unit(base + "/h", "rolehead", title, start, start + 1,
                                prefix="### ", role=role)
            if dates and dspan:
                role["datesu"] = unit(base + "/d", "roledates", dates,
                                      dspan[0], dspan[1], role=role)
            elif dates:
                role["datesu"] = None       # it rides on the heading line
            continue

        if t.startswith("- ") or t.startswith("* "):
            marker = t[:2]
            item = t[2:].strip()
            more, j = prose(i + 1)
            if more:
                item = (item + " " + more).strip()
            end = j if more else i + 1
            if role is not None:
                u = unit("%s/b%d" % (role["base"], len(role["bullets"])), "bullet",
                         item, i, end, marker=marker, role=role)
                role["bullets"].append(u)
                role["end"] = end
            else:
                own = owner_of(sec)
                if own["skills"]:
                    u = unit("", "group", item, i, end, marker=marker)
                    own["groups"].append(u)
                else:
                    u = unit("%s/%d" % (own["sid"], own["flat"]), "item", item, i, end,
                             marker=marker)
                    own["flat"] += 1
                    own["flats"].append(u)
            i = end
            continue

        m = LABELLED.match(t)
        if m and sec is not None:
            text, j = m.group(2).strip(), i + 1
            if text.endswith((";", ",")):
                more, j = prose(j)
                if more:
                    text = (text + " " + more).strip()
            label = m.group(1).strip()
            if sec["skills"]:
                u = unit("", "group", text, i, j, label=label,
                         prefix="**%s:** " % label)
                sec["groups"].append(u)
            else:
                u = unit("%s/%d" % (sec["sid"], sec["flat"]), "labelled", text, i, j,
                         label=label, prefix="**%s:** " % label)
                sec["flat"] += 1
                sec["flats"].append(u)
            role = None
            i = j
            continue

        if sec is None:
            unit("contact/%d" % sum(1 for u in units if u["kind"] == "contact"),
                 "contact", t, i, i + 1)
            i += 1
            continue

        text, j = prose(i)
        if role is not None and not role["bullets"]:
            u = unit("%s/s%d" % (role["base"], len(role["scope"])), "scope", text, i, j,
                     role=role)
            role["scope"].append(u)
            role["end"] = j
        elif sec["skills"]:
            sec["groups"].append(unit("", "group", text, i, j))
            role = None
        else:
            unit("%s/%d" % (sec["sid"], sec["flat"]), "para", text, i, j)
            sec["flat"] += 1
            sec["flats"].append(units[-1])
            role = None
        i = j

    _group_ids(sections)
    return {"lines": lines, "units": units, "sections": sections, "notes": notes}


def _group_ids(sections):
    """The skills groups' ids, exactly as `render_cv._ids` gives them out.

    The prefix is the literal `key-skills/`, not the section's own slug, because that
    is what the renderer and the studio both use however the heading is spelled.
    """
    for sec in sections:
        if not sec["skills"]:
            continue
        seen = {}
        for k, g in enumerate(sec["groups"]):
            s = R.slug(g.get("label"))
            if not s:
                g["id"] = "key-skills/group-%d" % (k + 1)
                continue
            seen[s] = seen.get(s, 0) + 1
            g["id"] = ("key-skills/" + s if seen[s] == 1
                       else "key-skills/%s-%d" % (s, seen[s]))


# ------------------------------------------------------------------ emitting

def _wrap(lead, prefix, text, cont, width):
    """One line, or the same line wrapped the way this file wraps its lines.

    Only a line that arrived wrapped is wrapped again, and only at the column this
    file already wraps at, so a rewritten bullet sits in the page the way its
    neighbours do and a diff against the source shows the words that changed rather
    than every line of the paragraph.
    """
    first = lead + prefix + text
    if not width or len(first) <= width:
        return [first]
    got = textwrap.wrap(text, width=width, initial_indent=lead + prefix,
                        subsequent_indent=(cont if cont is not None
                                           else lead + "  "),
                        break_long_words=False, break_on_hyphens=False)
    if not got:
        return [first]
    for line in got[1:]:
        if LOOKS_LIKE_MARKUP(line.strip()):
            return [first]
    return got


def _render_unit(u, text, wrapw):
    """The raw markdown lines one unit becomes, given the wording it now carries."""
    width = wrapw if u.get("wrapped") else 0
    if u["kind"] == "name":
        return [u["lead"] + "# " + text]
    if u["kind"] == "contact":
        return [u["lead"] + text]
    if u["kind"] == "rolehead":
        role = u["role"]
        if role["dates_in_head"] and not R.d_removed(role["base"] + "/d"):
            d = R.d_text(role["base"] + "/d", role["dates"])
            if "|" in text:
                # a rewritten title with a pipe in it would be read back as the date
                # separator, so the date goes on its own line instead
                return [u["lead"] + "### " + text, u["lead"] + d]
            return [u["lead"] + "### " + text + " | " + d]
        return [u["lead"] + "### " + text]
    if u["kind"] == "roledates":
        return [u["lead"] + text]
    if u["kind"] in ("bullet", "item"):
        return _wrap(u["lead"], u.get("marker") or "- ", text, u.get("cont"), width)
    if u["kind"] in ("labelled", "group") and u.get("label"):
        return _wrap(u["lead"], "**%s:** " % u["label"], text, u.get("cont"), width)
    if u["kind"] == "group" and u.get("marker"):
        return _wrap(u["lead"], u["marker"], text, u.get("cont"), width)
    return _wrap(u["lead"], "", text, u.get("cont"), width)


def _new_text(u):
    """What this unit says now, whether the wording changed, and whether the line did.

    The two are not the same thing on a role heading that carries its dates after a
    pipe: `### Title | 2019 to 2023` is one line holding two addressable things, so a
    decision about the dates alone rewrites the line without touching the title.
    """
    if u["kind"] == "group":
        items = R.split_items(u["text"])
        got = R.strip_heading(u.get("label"), R.d_text(u["id"], u["text"], items))
    else:
        got = R.d_text(u["id"], u["text"])
    changed = _flat(got) != _flat(u["text"])
    redraw = changed
    if u["kind"] == "rolehead" and u["role"]["dates_in_head"]:
        base = u["role"]["base"]
        if R.d_removed(base + "/d"):
            redraw = True
        elif _flat(R.d_text(base + "/d", u["role"]["dates"])) != _flat(
                u["role"]["dates"]):
            redraw = True
    return got, changed, redraw


def _added_lines(uid, anchor, wrapw):
    """[(their wording, the markdown lines it becomes)], in the shape of its neighbour.

    A line added under a bullet is written as a bullet, one added under a contact line
    as a contact line, so the file reads as if they had typed it there themselves.
    """
    out = []
    for k, t in enumerate(R.d_adds(uid)):
        if R.d_removed("%s/+%d" % (uid, k)):
            continue
        kind = anchor["kind"] if anchor else "item"
        cont = anchor.get("cont") if anchor else None
        if kind in ("bullet", "item"):
            got = _wrap(anchor["lead"], anchor.get("marker") or "- ", t, cont, wrapw)
        elif kind == "contact":
            got = [anchor["lead"] + t]
        else:
            got = _wrap(anchor["lead"] if anchor else "", "", t, cont, wrapw)
            if kind == "para":
                # An added profile paragraph must not merge into its neighbour
                # when the Markdown is scanned or rendered again.
                got = [""] + got + [""]
        out.append((t, got))
    return out


def _extra_section(spec, shout, heading, wrapw):
    """A ticked extra section, written into the markdown as a real section."""
    title = spec.get("title") or "Added section"
    out = [heading + " " + (title.upper() if shout else title)]
    for x in spec.get("lines") or []:
        key, text = x.get("key"), (x.get("text") or "").strip()
        if not text or (key and R.d_removed(key)):
            continue
        if key:
            text = R.d_text(key, text)
        if spec.get("format") == "paragraphs":
            out += [""] + _wrap("", "", text, "", wrapw)
        else:
            out += _wrap("", "- ", text, "  ", wrapw)
    return out if len(out) > 1 else []


def assemble(md, d, source_name="", decisions_name="", variant="", when=None):
    """The assembled markdown, and the record of what went into it."""
    keep = {k: R.DECIDE[k] for k in R.DECIDE}
    R.DECIDE["marks"] = (d or {}).get("marks") or {}
    R.DECIDE["adds"] = (d or {}).get("adds") or {}
    R.DECIDE["sections"] = (d or {}).get("sections") or []
    R.DECIDE["order"] = (d or {}).get("order") or {}
    R.DECIDE["section_order"] = (d or {}).get("section_order") or []
    try:
        return _assemble(md, d, source_name, decisions_name, variant, when)
    finally:
        R.DECIDE.clear()
        R.DECIDE.update(keep)


def _assemble(md, d, source_name, decisions_name, variant, when):
    when = when or datetime.datetime.now()
    # A CV that has been through Word on a Windows machine ends its lines with CRLF.
    # The work happens on plain newlines and the file goes back out the way it came in,
    # so a Windows file stays a Windows file. A file with both endings in it comes out
    # with the one it mostly used.
    crlf = "\r\n" in md
    if crlf:
        md = md.replace("\r\n", "\n")
    eff = R.effect(d)
    section_order = eff.get("section_order", [])
    if section_order:
        parts = re.split(r"(?m)(?=^## )", md)
        preamble, bodies = parts[0], parts[1:]
        by_slug = {R.slug(body.split("\n", 1)[0][3:].strip()): body for body in bodies}
        if len(by_slug) != len(bodies) or sorted(section_order) != sorted(by_slug):
            raise ValueError("The section order must name each source heading exactly once.")
        md = preamble + "".join(by_slug[s].rstrip("\n") + "\n\n" for s in section_order)
    S = scan(md)
    lines, units, sections = S["lines"], S["units"], S["sections"]
    by_id = {}
    for u in units:
        if u["id"]:
            by_id.setdefault(u["id"], u)

    # the column this file wraps at, read off the lines that already wrap. A file that
    # wraps nothing gives 0, and then nothing written into it is wrapped either.
    wrapw = max([u["width"] for u in units if u["wrapped"]] or [0])
    heading = "##"
    shout_titles = [s["title"] for s in sections if s["title"]]
    shout = bool(shout_titles) and all(t == t.upper() for t in shout_titles)

    # the wording, the removals and the additions, resolved once
    R.REORDERED.clear()
    del R.APPLIED[:]

    # which unit's content prints in which unit's slot
    content_at = {}
    for u in units:
        if u["id"]:
            content_at[u["id"]] = u
    for sec in sections:
        if not sec["skills"] and sec["flats"]:
            seq = R.d_seq(sec["sid"], len(sec["flats"]))
            for slot, take in enumerate(seq):
                content_at[sec["flats"][slot]["id"]] = sec["flats"][take]
        for role in sec["roles"]:
            if role["bullets"]:
                seq = R.d_seq(role["base"], len(role["bullets"]))
                for slot, take in enumerate(seq):
                    content_at[role["bullets"][slot]["id"]] = role["bullets"][take]

    # A role comes off whole when its heading does, which is what the renderer does
    # too. Its dates, its scope and every one of its bullets go with it, and every one
    # of them is named in the archive, because "the role went" is not an answer to
    # "where did that line go".
    suppress, with_role = set(), {}
    for sec in sections:
        for role in sec["roles"]:
            if R.d_removed(role["base"] + "/h"):
                for k in range(role["start"], role["end"]):
                    suppress.add(k)
                for u in [role["head"], role.get("datesu")] + role["scope"] \
                        + role["bullets"]:
                    if u is not None and u["id"] != role["base"] + "/h":
                        with_role[u["id"]] = role["base"] + "/h"
    for k in S["notes"]:
        suppress.add(k)

    starts = {u["start"]: u for u in units}
    inside = set()
    for u in units:
        for k in range(u["start"] + 1, u["end"]):
            inside.add(k)

    record = {"edited": [], "removed": [], "added": [], "sections": [],
              "orphans": []}
    pending_after, pending_end = {}, []
    for spec in eff["sections"]:
        after = (spec.get("after") or "").strip().lower()
        if after == "^" or (after and any(s["sid"] == after for s in sections)):
            pending_after.setdefault(after, []).insert(0, spec)
        else:
            pending_end.append(spec)

    out, done_after = [], set()
    just_dropped = False

    def flush(sid):
        """The extra sections that go after this one, with one blank line either side."""
        if sid in done_after:
            return
        done_after.add(sid)
        for spec in pending_after.get(sid, []):
            body = _extra_section(spec, shout, heading, wrapw)
            if not body:
                continue
            while out and not out[-1].strip():
                out.pop()
            out.append("")
            out.extend(body)
            out.append("")
            record["sections"].append(spec.get("title") or "Added section")

    last_sid = None
    i, n = 0, len(lines)
    while i < n:
        if i in suppress:
            gone = starts.get(i)
            if gone is not None and gone["id"]:
                gone["with_role"] = with_role.get(gone["id"])
                record["removed"].append(gone)
            just_dropped = True
            i += 1
            continue
        if i in inside:
            i += 1
            continue
        u = starts.get(i)
        if u is None:
            t = lines[i].strip()
            if t.startswith("## ") and last_sid is not None:
                flush(last_sid)
            if t.startswith("## "):
                if last_sid is None:
                    flush("^")
                last_sid = R.slug(t[3:].strip()) or "section"
            if not t and just_dropped and out and not out[-1].strip():
                i += 1
                continue
            if t:
                just_dropped = False
            out.append(lines[i])
            i += 1
            continue

        src = content_at.get(u["id"], u)
        if R.d_removed(src["id"]):
            record["removed"].append(src)
            just_dropped = True
            i = u["end"]
            continue

        text, changed, redraw = _new_text(src)
        if changed:
            record["edited"].append((src, text))
        if redraw:
            out.extend(_render_unit(src, text, wrapw))
        elif src is u:
            out.extend(lines[u["start"]:u["end"]])
        else:
            out.extend(src["raw"])
        for text_of, got in _added_lines(src["id"], src, wrapw):
            record["added"].append((src["id"], text_of))
            out.extend(got)
        just_dropped = False
        i = u["end"]

    if last_sid is not None:
        flush(last_sid)
    for spec in pending_end:
        body = _extra_section(spec, shout, heading, wrapw)
        if body:
            while out and not out[-1].strip():
                out.pop()
            out.append("")
            out.extend(body)
            out.append("")
            record["sections"].append(spec.get("title") or "Added section")

    # What the decisions file asked for that this CV has no line for. A role that keeps
    # its dates after a pipe has no date line of its own, and `<role>/d` still addresses
    # something, so it counts as present.
    known = set(by_id)
    for sec in sections:
        for g in sec["groups"]:
            if g.get("id"):
                known.add(g["id"])
        for role in sec["roles"]:
            if role["dates_in_head"]:
                known.add(role["base"] + "/d")
    for key in sorted(eff["marks"]):
        if key not in known:
            record["orphans"].append(("mark", key))
    for key in sorted(eff["adds"]):
        if key not in known:
            record["orphans"].append(("add", key))

    record["reordered"] = dict(R.REORDERED)
    body = "\n".join(out)

    prior = R.read_note(md)
    baked = list((prior or {}).get("baked") or [])
    if any(eff.values()):
        entry = {
            "file": decisions_name or "cv-decisions.json",
            "saved": (d.get("saved") or "") if isinstance(d, dict) else "",
            "sha256": R.digest(d),
            "at": when.strftime("%Y-%m-%dT%H:%M:%S"),
            "source": source_name,
            "ids": {
                "edited": sorted(k for k, m in eff["marks"].items() if m["a"] == "edit"),
                "removed": sorted(k for k, m in eff["marks"].items()
                                  if m["a"] == "remove"),
                "added": sorted(eff["adds"]),
                "ordered": sorted(eff["order"]),
                "sections": [s["title"] for s in eff["sections"]],
            },
        }
        baked = [x for x in baked if x.get("sha256") != entry["sha256"]] + [entry]
        note = {"resu_studio": "assembled", "v": 1, "baked": baked}
        if variant:
            note["variant"] = variant
        body = body.rstrip("\n") + "\n\n" + R.note_line(note) + "\n"
        record["note"] = note
    elif prior:
        record["note"] = prior
    if crlf:
        body = body.replace("\n", "\r\n")
    return body, record


# ------------------------------------------------------------------ verifying

def outline(md, d):
    """What this markdown plus these decisions puts on the page, line by line.

    Layout, skin and column are not in it. It is the words, in the order they print,
    which is the only thing assembling is allowed to change, so comparing the outline
    of the source plus the decisions against the outline of the assembled file with
    no decisions at all is a proof that the two routes say the same thing.
    """
    keep = {k: R.DECIDE[k] for k in R.DECIDE}
    try:
        R.DECIDE["marks"] = (d or {}).get("marks") or {}
        R.DECIDE["adds"] = (d or {}).get("adds") or {}
        R.DECIDE["sections"] = (d or {}).get("sections") or []
        R.DECIDE["order"] = (d or {}).get("order") or {}
        R.DECIDE["section_order"] = (d or {}).get("section_order") or []
        doc = R.parse(md)
        R.add_sections(doc)
        out = []
        if not R.d_removed("name/0"):
            out.append("name:" + _flat(R.d_text("name/0", doc["name"])))
        for k, c in enumerate(doc["contact"]):
            i = "contact/%d" % k
            if not R.d_removed(i):
                out.append("line:" + _flat(R.d_text(i, c)))
            for j, t in enumerate(R.d_adds(i)):
                if not R.d_removed("%s/+%d" % (i, j)):
                    out.append("line:" + _flat(t))
        for s in doc["sections"]:
            title = s["title"]
            if title:
                out.append("section:" + _flat(title).lower())
            sid = R.slug(title) or "section"
            if s.get("added"):
                for k, b in enumerate(s["blocks"]):
                    i = b.get("id") or ("%s/%d" % (sid, k))
                    if not R.d_removed(i):
                        out.append("line:" + _flat(R.d_text(i, b["text"])))
                continue
            if R.is_skills(title):
                for g in R.skill_groups(s["blocks"]):
                    gid = g["gid"]
                    if R.d_removed(gid):
                        continue
                    text = R.strip_heading(
                        g["label"], R.d_text(gid, g["orig"], g["items"]))
                    out.append("skills:%s|%s" % (_flat(g["label"]).lower(),
                                                 _flat(text)))
                continue
            flat = [b for b in s["blocks"] if b["kind"] != "role"]
            fseq, fat, ri = R.d_seq(sid, len(flat)), 0, 0
            for blk in s["blocks"]:
                if blk["kind"] == "role":
                    base = "%s/%d" % (sid, ri)
                    ri += 1
                    if R.d_removed(base + "/h"):
                        continue
                    out.append("role:" + _flat(R.d_text(base + "/h", blk["title"])))
                    if blk["dates"] and not R.d_removed(base + "/d"):
                        out.append("dates:" + _flat(R.d_text(base + "/d",
                                                             blk["dates"])))
                    for j, p in enumerate(blk["scope"]):
                        k = "%s/s%d" % (base, j)
                        if not R.d_removed(k):
                            out.append("line:" + _flat(R.d_text(k, p)))
                    for j in R.d_seq(base, len(blk["bullets"])):
                        k = "%s/b%d" % (base, j)
                        if not R.d_removed(k):
                            out.append("line:" + _flat(R.d_text(k, blk["bullets"][j])))
                        for m, t in enumerate(R.d_adds(k)):
                            if not R.d_removed("%s/+%d" % (k, m)):
                                out.append("line:" + _flat(t))
                    continue
                bi = fseq[fat]
                b = flat[bi]
                fat += 1
                k = "%s/%d" % (sid, bi)
                if not R.d_removed(k):
                    lab = (_flat(b["label"]) + " ") if b["kind"] == "labelled" else ""
                    out.append("line:" + lab + _flat(R.d_text(k, b["text"])))
                for m, t in enumerate(R.d_adds(k)):
                    if not R.d_removed("%s/+%d" % (k, m)):
                        out.append("line:" + _flat(t))
        return out
    finally:
        R.DECIDE.clear()
        R.DECIDE.update(keep)


def verify(source_md, d, built_md):
    """The first difference between what the two routes print, or None."""
    want, got = outline(source_md, d), outline(built_md, {})
    for k in range(max(len(want), len(got))):
        a = want[k] if k < len(want) else "(nothing)"
        b = got[k] if k < len(got) else "(nothing)"
        if a != b:
            return (k, a, b)
    return None


# ------------------------------------------------------------------ the archive

def _reason(mark, props):
    """Why a line came off, in the person's terms, if the file says."""
    bits = []
    for key in ("reason", "why", "note"):
        if mark.get(key):
            bits.append(str(mark[key]).strip())
            break
    p = mark.get("p")
    if p:
        rec = props.get(p) or {}
        if not bits and rec.get("note"):
            bits.append(str(rec["note"]).strip())
        bits.append("proposal %s" % p)
    return ", ".join(bits)


def _quote(text):
    return "\n".join("> " + x for x in textwrap.wrap(_flat(text), 86)) or "> "


def archive_block(record, d, out_name, source_name, decisions_name, when, passno):
    """One pass, written for a person who is wondering where a line went."""
    props = {}
    for rec in (d.get("proposals") or []):
        if isinstance(rec, dict) and rec.get("p"):
            props[rec["p"]] = rec
    marks = d.get("marks") or {}
    day = when.strftime("%d %B %Y").lstrip("0")

    L = ["", "## Pass %d: %s" % (passno, day), ""]
    L.append("`%s` assembled from `%s` with `%s`%s."
             % (out_name, source_name, decisions_name,
                (", saved " + d["saved"]) if d.get("saved") else ""))
    L.append("")

    gone = record["removed"]
    L.append("### Taken off this version: %d line%s"
             % (len(gone), "" if len(gone) == 1 else "s"))
    L.append("")
    if not gone:
        L += ["Nothing was taken off in this pass.", ""]
    for u in gone:
        m = marks.get(u["id"]) or {}
        where = (m.get("where") or "").strip()
        why = _reason(m, props)
        if u.get("with_role"):
            why = ("the whole role was taken off, at %s" % u["with_role"]) \
                + ((", " + why) if why else "")
        L.append("**%s**%s. Taken off %s.%s"
                 % (u["id"], (", under " + where) if where else "", day,
                    (" Reason: " + why + ".") if why else ""))
        L.append("")
        L.append(_quote(m.get("was") or u["text"]))
        L.append("")

    edits = record["edited"]
    L.append("### Rewritten: %d line%s" % (len(edits), "" if len(edits) == 1 else "s"))
    L.append("")
    if not edits:
        L += ["Nothing was rewritten in this pass.", ""]
    for u, text in edits:
        m = marks.get(u["id"]) or {}
        where = (m.get("where") or "").strip()
        whose = "in their own words" if m.get("from") not in ("claude", "claude-edited") \
            else "from a suggestion they accepted"
        L.append("**%s**%s. Rewritten %s, %s."
                 % (u["id"], (", under " + where) if where else "", day, whose))
        L.append("")
        L.append("Before:")
        L.append("")
        L.append(_quote(m.get("was") or u["text"]))
        L.append("")
        L.append("After:")
        L.append("")
        L.append(_quote(text))
        L.append("")

    if record["added"]:
        L.append("### Lines they added: %d" % len(record["added"]))
        L.append("")
        for uid, text in record["added"]:
            L.append("**after %s**:" % uid)
            L.append("")
            L.append(_quote(text))
            L.append("")
    if record["reordered"]:
        L.append("### Lists put in their order: %d" % len(record["reordered"]))
        L.append("")
        for key in sorted(record["reordered"]):
            L.append("- `%s` now reads in the original line order %s."
                     % (key, ", ".join(str(x) for x in record["reordered"][key])))
        L.append("")
    if record["sections"]:
        L.append("### Sections written in: %d" % len(record["sections"]))
        L.append("")
        for t in record["sections"]:
            L.append("- %s" % t)
        L.append("")
    return "\n".join(L).rstrip("\n") + "\n"


ARCHIVE_HEAD = """# Archive for %s

Every line taken off this version, and every line rewritten, kept here in full with
the wording it had before. Nothing on this page is deleted: it is off one CV, and it
can be put back by hand at any time.

Written by `scripts/assemble.py`, and appended to on every pass. Nothing here is ever
rewritten or removed.
"""


def write_archive(path, record, d, out_name, source_name, decisions_name, when):
    passno = 1
    head = ""
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            old = f.read()
        passno = len(re.findall(r"^## Pass \d+", old, re.M)) + 1
        body = old.rstrip("\n") + "\n"
    else:
        head = ARCHIVE_HEAD % out_name
        body = head
    block = archive_block(record, d, out_name, source_name, decisions_name, when,
                          passno)
    with open(path, "a" if head == "" else "w", encoding="utf-8") as f:
        if head:
            f.write(body)
        f.write("\n" + block)
    return passno


# ------------------------------------------------------------------ the audit

def audit(md, d, cv_name="the CV", decisions_name="cv-decisions.json",
          source_name=None, folder=None):
    """Where an assembled CV and a decisions file disagree, in plain words.

    This is the check that would have caught the whole thing: a markdown that still
    holds a line the decisions file takes off, or is missing a line the person added,
    is a markdown that is not the document, however good the PDF looked.
    """
    out = []
    eff = R.effect(d)
    if not any(eff.values()):
        return out
    note = R.read_note(md)
    baked_ids = {"edited": set(), "removed": set(), "added": set(), "ordered": set(),
                 "sections": set()}
    shas = set()
    for e in ((note or {}).get("baked") or []):
        shas.add(e.get("sha256"))
        for k in baked_ids:
            baked_ids[k].update((e.get("ids") or {}).get(k) or [])
        f = e.get("file")
        if f and folder and not os.path.isfile(os.path.join(folder, f)):
            out.append("%s says it was assembled from %s, and there is no %s in this "
                       "folder. The record of what was baked into this CV is not "
                       "beside it, so nothing can tell whether it is up to date. Put "
                       "the decisions file back, or assemble the CV again from its "
                       "source." % (cv_name, f, f))
    fix = ("Run: python3 scripts/assemble.py %s --decisions %s --out %s"
           % (source_name or "<the source cv markdown>", decisions_name, cv_name))

    S = scan(md)
    by_id, texts = {}, []
    for u in S["units"]:
        if u["id"]:
            by_id.setdefault(u["id"], u)
        texts.append(_flat(u["text"]))
    for sec in S["sections"]:
        for g in sec["groups"]:
            if g.get("id"):
                by_id.setdefault(g["id"], g)
    have = set(texts)

    if R.digest(d) in shas:
        return out                        # this CV is exactly these decisions

    for key, m in sorted(eff["marks"].items()):
        u = by_id.get(key)
        if m["a"] == "remove":
            if u is not None and key not in baked_ids["removed"]:
                out.append("%s still holds the line %s takes off (%s: %r). The "
                           "markdown is meant to be the document, and this one is not "
                           "it. %s" % (cv_name, decisions_name, key,
                                       _flat(u["text"])[:70], fix))
        elif m["a"] == "edit" and m.get("text"):
            # Only when the line still says exactly what it said before the rewrite.
            # A line that says neither the old wording nor the new one has been edited
            # by hand since, and telling somebody their own later edit is a fault is
            # how they stop reading the output.
            was = _flat(((d.get("marks") or {}).get(key) or {}).get("was") or "")
            if (u is not None and key not in baked_ids["edited"] and was
                    and _flat(u["text"]) != _flat(m["text"])
                    and _flat(u["text"]) == was):
                out.append("%s still has the old wording of %s, and %s rewrites it in "
                           "the person's own words. %s"
                           % (cv_name, key, decisions_name, fix))
    for key, lst in sorted(eff["adds"].items()):
        for t in lst:
            if _flat(t) not in have and key not in baked_ids["added"]:
                out.append("the line added after %s is not in %s: %r. A line the "
                           "person wrote is missing from the file they hand over. %s"
                           % (key, cv_name, _flat(t)[:70], fix))
    for spec in eff["sections"]:
        want = _flat(spec["title"]).lower()
        titles = [_flat(s["title"]).lower() for s in S["sections"]]
        if want not in titles and want not in {_flat(x).lower()
                                               for x in baked_ids["sections"]}:
            out.append("%s ticks the section %r and %s has no such section. %s"
                       % (decisions_name, spec["title"], cv_name, fix))

    # the other direction: offering decisions that are already in the file
    dup_adds = sorted(set(eff["adds"]) & baked_ids["added"])
    dup_order = sorted(set(eff["order"]) & baked_ids["ordered"])
    if dup_adds or dup_order:
        out.append("%s is already assembled, and %s carries %s that %s already holds. "
                   "Rendering the two together would print the added line twice and "
                   "apply the order a second time. Build a fresh studio from %s and "
                   "make any new decisions against that."
                   % (cv_name, decisions_name,
                      " and ".join(x for x in
                                   ["the additions under " + ", ".join(dup_adds)
                                    if dup_adds else "",
                                    "the order for " + ", ".join(dup_order)
                                    if dup_order else ""] if x),
                      cv_name, cv_name))
    return out


# ------------------------------------------------------------------ main

def _variant_of(path):
    stem = os.path.basename(os.path.splitext(path or "")[0])
    return stem[3:] if stem.startswith("cv-") else stem


def main():
    ap = argparse.ArgumentParser(
        description="Bake a cv-decisions.json into a CV markdown, so the markdown "
                    "is the whole document.")
    ap.add_argument("cv", help="the source CV markdown the decisions were made about")
    ap.add_argument("--decisions", required=True,
                    help="the cv-decisions.json the studio saved")
    ap.add_argument("--out", required=True,
                    help="the assembled markdown to write, normally cv-<variant>.md")
    ap.add_argument("--archive", default=None,
                    help="where the record of everything taken off and every rewrite "
                         "goes. Default: cv-<variant>-archive.md beside --out")
    ap.add_argument("--variant", default=None,
                    help="the name of this version. Default: read off --out")
    ap.add_argument("--no-archive", action="store_true", dest="no_archive",
                    help="do not write the archive. Only for a run that is being "
                         "thrown away: a removal with no archive is a deletion")
    a = ap.parse_args()

    for path, what in ((a.cv, "cv markdown"), (a.decisions, "decisions file")):
        if not os.path.isfile(path):
            sys.stderr.write("no %s at %s\n" % (what, path))
            return 2
    with open(a.cv, encoding="utf-8", newline="") as f:
        md = f.read()
    try:
        with open(a.decisions, encoding="utf-8") as f:
            d = json.load(f)
    except ValueError as exc:
        sys.stderr.write("REFUSING TO WRITE. %s is not valid JSON: %s. It is usually a "
                         "missing comma, a trailing comma or a quote that did not get "
                         "pasted.\n" % (a.decisions, exc))
        return 1
    wrong = R._decisions_wrong(d)
    if wrong:
        sys.stderr.write("REFUSING TO WRITE. In %s, %s\n" % (a.decisions, wrong))
        return 1

    if d.get("writing"):
        if os.path.normcase(os.path.abspath(a.out)) == os.path.normcase(os.path.abspath(a.cv)):
            sys.stderr.write("REFUSING TO WRITE. Each writing round needs a distinct output filename so its reviewed source stays intact.\n")
            return 1
        import writing
        try:
            state = writing.load(d["writing"]["job"])
            faults = writing.decision_faults(d, state, a.cv) if state else ["This application's writing record is missing."]
        except (ValueError, OSError, KeyError) as exc:
            faults = [str(exc)]
        if faults:
            sys.stderr.write("REFUSING TO WRITE. " + "\n".join(faults) + "\n")
            return 1

    # Writing over the source would destroy the only copy of what arrived, and the
    # archive points at it by name. A file that has already been assembled is a
    # different case: it is a version, not the source, so a second pass may land on it.
    if (os.path.abspath(a.out) == os.path.abspath(a.cv)
            and not R.read_note(md)):
        sys.stderr.write(
            "REFUSING TO WRITE. --out is %s, which is the file being assembled from. "
            "That file is the record of what arrived and the archive names it, so it "
            "has to stay as it is. Write the assembled CV to its own name, normally "
            "cv-<variant>.md.\n" % a.cv)
        return 1

    doc = R.parse(md)
    src, got = R.count_source(md), R.count_doc(doc)
    if src != got:
        sys.stderr.write("REFUSING TO WRITE. %d content lines in %s, %d accounted for. "
                         "Something would have been dropped.\n" % (src, a.cv, got))
        return 1
    if d.get("order"):
        bad = R.order_faults(d["order"], R.order_lists(doc))
        if bad:
            sys.stderr.write("REFUSING TO WRITE. In %s, %s\n" % (a.decisions, bad))
            return 1

    variant = a.variant or _variant_of(a.out)
    when = datetime.datetime.now()
    body, record = assemble(md, d, source_name=os.path.basename(a.cv),
                            decisions_name=os.path.basename(a.decisions),
                            variant=variant, when=when)

    bad = verify(md, d, body)
    if bad:
        k, want, gotline = bad
        sys.stderr.write(
            "REFUSING TO WRITE. The assembled markdown does not print what the source "
            "plus the decisions print. At line %d of the page, the decisions give\n"
            "  %s\nand the assembled file gives\n  %s\nNothing was written. This is a "
            "fault in assemble.py, not in your CV: send both files with this "
            "message.\n" % (k + 1, want, gotline))
        return 1

    with open(a.out, "w", encoding="utf-8", newline="") as f:
        f.write(body)

    apath = a.archive or os.path.join(os.path.dirname(os.path.abspath(a.out)),
                                      "cv-%s-archive.md" % variant)
    wrote_archive = None
    if not a.no_archive and (record["removed"] or record["edited"]
                             or record["added"] or record["reordered"]
                             or record["sections"]):
        write_archive(apath, record, d, os.path.basename(a.out),
                      os.path.basename(a.cv), os.path.basename(a.decisions), when)
        wrote_archive = apath

    print("wrote %s" % a.out)
    print("  from %s, with %s%s"
          % (os.path.basename(a.cv), os.path.basename(a.decisions),
             (", saved " + d["saved"]) if d.get("saved") else ""))
    bits = []
    for count, one, many in ((len(record["edited"]), "rewrite", "rewrites"),
                             (len(record["removed"]), "line taken off",
                              "lines taken off"),
                             (len(record["added"]), "line added", "lines added"),
                             (len(record["reordered"]), "list reordered",
                              "lists reordered"),
                             (len(record["sections"]), "section written in",
                              "sections written in")):
        if count:
            bits.append("%d %s" % (count, one if count == 1 else many))
    print("  %s" % (", ".join(bits) if bits
                    else "nothing to bake in: this is a copy of the source"))
    if record["removed"]:
        for u in record["removed"]:
            print("    - [%s] %s" % (u["id"], _flat(u["text"])[:88]))
    for uid, text in record["added"]:
        print("    + [after %s] %s" % (uid, _flat(text)[:88]))
    for key in sorted(record["reordered"]):
        print("    ~ [%s] now prints as %s"
              % (key, ", ".join(str(x) for x in record["reordered"][key])))
    for t in record["sections"]:
        print("    + [section] %s" % t)
    for kind, key in record["orphans"]:
        sys.stderr.write("the decisions file has a%s for %r, and this CV has no such "
                         "line. Nothing was %s for it.\n"
                         % (" mark" if kind == "mark" else "n addition", key,
                            "changed" if kind == "mark" else "added"))
    if wrote_archive:
        print("  archive: %s" % wrote_archive)
        print("    it holds every line taken off, in full, and both wordings of every "
              "rewrite. A removal is not a deletion.")
    if record.get("note"):
        print("  the foot of the file carries a one line note saying which decisions "
              "are baked in. It never prints and it is not counted.")
        print("  render it with no --decisions at all: everything is in the markdown "
              "now.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
