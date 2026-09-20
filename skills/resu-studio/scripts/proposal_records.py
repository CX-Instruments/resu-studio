"""Read one proposal contract for writing, the Studio and validation.

Old proposals remain readable. Engine-published proposals additionally explain
their purpose and account for every clause through a claim map. Structural checks
do not establish that a source supports a meaning; that remains the agent's review.
"""

import hashlib
import json
import re

FIELDS = {"currently": "cur", "suggested": "sug", "line": "line",
          "why": "why", "answers": "answers", "draws on": "draws",
          "draws_on": "draws", "costs": "costs", "question": "q",
          "purpose": "purpose", "claims": "claims", "kind": "label",
          "order": "order", "section": "section"}
PURPOSES = {"relevance", "evidence visibility", "comprehension", "differentiation",
            "voice", "economy", "accuracy", "structure"}


def norm(value):
    return " ".join(str(value or "").split())


def parse(text):
    result = []
    for block in re.split(r"(?m)^##\s+(?=P\d+[.: ])", text)[1:]:
        first, _, body = block.partition("\n")
        match = re.match(r"(P\d+)[.:]?\s*(.*)", first)
        rec = {"p": match[1], "where": match[2]}
        fields = re.split(r"(?m)^\*\*([\w ]+):\*\*\s*", body)
        for i in range(1, len(fields), 2):
            key = FIELDS.get(fields[i].lower())
            if key:
                value = fields[i + 1].strip()
                if key in ("claims", "order", "section"):
                    try:
                        value = json.loads(re.sub(r"^```(?:json)?\s*|\s*```$", "", value))
                    except ValueError:
                        value = None
                else:
                    value = norm(value)
                rec[key] = value
        rec["kind"] = ("section" if "section" in rec else "order" if "order" in rec else "remove" if rec.get("sug", "").lower().startswith("delete this")
                       else "add" if rec.get("cur", "").lower().startswith("not on the cv")
                       else "ask" if not rec.get("sug") else "edit")
        rec["uid"] = identity(rec)
        result.append(rec)
    return result


def identity(rec, context=""):
    value = {k: v for k, v in rec.items() if k not in ("uid", "p", "where")}
    return hashlib.sha256(json.dumps([context, value], sort_keys=True,
                                     ensure_ascii=False).encode("utf-8")).hexdigest()[:24]


def validate(records, cv, facts, asks, strict=False):
    import writing
    import render_cv
    known = writing.source_lines(cv)
    fids = writing.evidence_ids(facts)
    aids = writing.fact_ids(asks)
    faults, pids, targets = [], set(), set()
    with open(cv, encoding="utf-8-sig") as f:
        doc = render_cv.parse(f.read())
    for rec in records:
        prefix = "%s: " % rec["p"]
        def fail(message):
            faults.append(prefix + message)
        if rec["p"] in pids:
            fail("The proposal id is repeated.")
        pids.add(rec["p"])
        line = rec.get("line", "")
        if line in targets and rec["kind"] != "ask":
            fail("Two changes target the same slot. Offer one reviewable change per slot.")
        targets.add(line)
        if not rec.get("why") or "cur" not in rec:
            fail("Every proposal needs current text and a reason.")
        if rec["kind"] == "section":
            spec = rec.get("section")
            slugs = {render_cv.slug(s["title"]) for s in doc["sections"]}
            if not isinstance(spec, dict) or not spec.get("title") or not spec.get("lines"):
                fail("Section needs title, slug, after, format and lines.")
            elif (spec.get("slug") != render_cv.slug(spec["title"]) or spec["slug"] in slugs
                  or line != "new-section/" + spec["slug"]
                  or spec.get("format") not in ("paragraphs", "bullets")
                  or (spec.get("after") and spec["after"] not in slugs | {"^"})):
                fail("The new section needs a unique slug, valid placement and paragraph or bullet format.")
            elif norm(" ".join(x.get("text", "") for x in spec["lines"])) != norm(rec.get("sug")):
                fail("Suggested must contain all new section text in order.")
            if not rec.get("costs"):
                fail("A new section needs an explicit space cost.")
        elif rec["kind"] == "order":
            if not isinstance(rec.get("order"), list):
                fail("Order must be a JSON list of original indices.")
            elif line == "document/sections":
                slugs = [render_cv.slug(s["title"]) for s in doc["sections"]]
                if sorted(rec["order"]) != sorted(slugs):
                    fail("A section order must name every source section exactly once.")
            else:
                lists = render_cv.order_lists(doc)
                if line not in lists:
                    fail("That list does not exist in this CV.")
                error = render_cv.order_faults({line: rec["order"]}, lists)
                if error:
                    fail(error)
            if not rec.get("sug"):
                fail("Describe the proposed order in Suggested so the person can review it.")
        elif line.split("/+")[0] not in known:
            fail("The target line does not exist in this CV.")
        elif rec["kind"] != "add" and norm(rec.get("cur")) != norm(known.get(line)):
            fail("Currently must match the source line exactly.")
        if rec["kind"] == "ask":
            if not rec.get("q"):
                fail("A question needs Question text.")
            continue
        if rec["kind"] == "add" and ("/+" not in line or not rec.get("costs")):
            fail("An addition needs an /+ index and an explicit space cost.")
        if rec["kind"] in ("edit", "add", "section"):
            refs = [x.strip() for x in rec.get("draws", "").split(",") if x.strip()]
            if not refs or any(r not in fids for r in refs):
                fail("Draws on must name existing facts.")
            ans = [x.strip() for x in rec.get("answers", "").split(",") if x.strip()]
            if any(r not in aids for r in ans):
                fail("Answers contains an unknown requirement.")
            if strict:
                try:
                    writing.claims_valid(rec["sug"], rec.get("claims"), fids)
                    if any(fid not in refs for c in rec["claims"] for fid in c["facts"]):
                        fail("Draws on must include every fact cited by the claim map.")
                except ValueError as exc:
                    fail(str(exc))
        if strict and rec.get("purpose") not in PURPOSES:
            fail("Choose a concrete Purpose: %s." % ", ".join(sorted(PURPOSES)))
        if rec.get("purpose") == "relevance" and not rec.get("answers"):
            fail("A relevance change needs the requirement it serves.")
    return faults
