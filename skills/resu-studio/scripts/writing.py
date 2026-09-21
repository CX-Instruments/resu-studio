"""Keep an application's writing direction and the requests made against it.

The host agent writes and reviews the language. This module keeps its inputs,
versions and decisions connected, so a page cannot authorise a different draft.
All personal material lives in the folder chosen through paths.py. No model API,
server or dependency is needed.
"""

import argparse
import copy
import datetime
import hashlib
import json
import os
import re
import shutil
import sys
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import paths
import writing_memory as memory

PILLARS = ("passion", "strengths", "impact", "value")
OBJECTIVES = ("pillars", "ats", "human", "tailoring", "integrity", "coherence", "constraints", "preservation")
MODE_FIELDS = ("name", "impression", "emphasis", "voice", "behaviour", "boundaries")
PHASES = {
    "choose": "Choose your writing mode",
    "preview_requested": "Your sample adjustments are with the AI",
    "rewrite_requested": "Your rewrite is with the AI",
    "review": "Review your suggested changes",
    "revision_requested": "Your revisions are with the AI",
    "review_required": "Review the remaining improvements",
    "ready": "Your CV is ready",
    "stale": "Refresh the writing samples for the changed inputs",
}


def read_json(path):
    with open(path, encoding="utf-8-sig") as f:
        return json.load(f)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def file_hash(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def norm(text):
    return " ".join(str(text or "").split())


def atomic(path, value):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    temp = path + "." + uuid.uuid4().hex + ".tmp"
    try:
        with open(temp, "w", encoding="utf-8", newline="\n") as f:
            json.dump(value, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.remove(temp)


def state_path(job):
    return os.path.join(paths.job_dir(job), "writing.json")


def load(job):
    path = state_path(job)
    return read_json(path) if os.path.isfile(path) else None


def save(job, state):
    """Keep each revision before replacing the current pointer."""
    state = copy.deepcopy(state)
    state["revision"] = uuid.uuid4().hex
    state["updated"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    archive = os.path.join(paths.job_dir(job), ".writing", state["revision"] + ".json")
    atomic(archive, state)
    atomic(state_path(job), state)
    try:
        import build_desk
        build_desk.refresh()
    except (ImportError, OSError):
        pass
    return state


def modes():
    shipped = read_json(os.path.join(HERE, "..", "assets", "writing-modes.json"))
    result = {m["id"]: m for m in shipped["modes"]}
    folder = os.path.join(paths.record_dir(), "writing-modes")
    if os.path.isdir(folder):
        for name in sorted(os.listdir(folder)):
            if not name.endswith(".json"):
                continue
            mode = read_json(os.path.join(folder, name))
            validate_mode(mode)
            prior = result.get(mode["id"])
            if not prior or mode["version"] > prior["version"]:
                result[mode["id"]] = mode
    return list(result.values())


def validate_mode(mode):
    if not isinstance(mode, dict):
        raise ValueError("A writing mode must be an object containing its guiding definition.")
    if not re.fullmatch(r"[a-z][a-z0-9-]{1,63}", str(mode.get("id", ""))):
        raise ValueError("A mode needs a stable lowercase id using letters, numbers and hyphens.")
    if type(mode.get("version")) is not int or mode["version"] < 1:
        raise ValueError("A mode needs a positive integer version.")
    for key in MODE_FIELDS:
        if not isinstance(mode.get(key), str) or not mode[key].strip():
            raise ValueError("The mode needs a nonempty %s." % key)


def save_mode(mode):
    validate_mode(mode)
    if not mode["id"].startswith("personal-"):
        raise ValueError("Personal mode ids start with personal- so they cannot replace a built-in mode.")
    target = os.path.join(paths.record_dir(), "writing-modes",
                          "%s-v%d.json" % (mode["id"], mode["version"]))
    if os.path.exists(target) and read_json(target) != mode:
        raise ValueError("That mode version already exists. Save the changed preference as a new version.")
    atomic(target, mode)
    return target


def source_record(cv, job):
    out = {}
    files = [("cv", cv), ("facts", paths.facts_file(job)),
             ("asks", os.path.join(paths.job_dir(job), "asks.md"))]
    ad = os.path.join(paths.job_dir(job), "ad")
    for folder, dirs, names in os.walk(ad):
        dirs.sort()
        for name in sorted(names):
            path = os.path.join(folder, name)
            files.append(("ad:" + os.path.relpath(path, ad), path))
    for key, path in files:
        path = os.path.abspath(path)
        if not os.path.isfile(path):
            raise ValueError("The %s file is missing at %s. Read the sources before preparing writing samples." % (key, path))
        sha = file_hash(path)
        snapshot = os.path.join(paths.job_dir(job), ".writing", "sources", sha + os.path.splitext(path)[1])
        os.makedirs(os.path.dirname(snapshot), exist_ok=True)
        if not os.path.exists(snapshot):
            shutil.copyfile(path, snapshot)
        out[key] = {"path": path, "hash": sha, "snapshot": snapshot}
    return out


def fact_blocks(path):
    with open(path, encoding="utf-8-sig") as f:
        text = f.read()
    blocks = re.findall(r"```(?:\w+)?\s*\n(.*?)```", text, re.S)
    if not blocks:
        blocks = re.split(r"(?m)(?=^id:)", text)
    out = {}
    for block in blocks:
        match = re.search(r"^id:\s*(\S+)\s*$", block, re.M)
        if match:
            out[match[1]] = norm(block)
    return out


def evidence_dependencies(state):
    ids = set()
    def visit(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key == "facts" and isinstance(item, list):
                    ids.update(x for x in item if isinstance(x, str))
                elif key == "draws" and isinstance(item, str):
                    ids.update(x.strip() for x in item.split(",") if x.strip())
                else:
                    visit(item)
        elif isinstance(value, list):
            for item in value:
                visit(item)
    for key in ("brief", "samples"):
        visit(state.get(key))
    batch = batch_for(state)
    if batch:
        visit(batch.get("records"))
    return ids


def stale(state):
    changed = []
    for key, src in state.get("sources", {}).items():
        if not os.path.isfile(src["path"]):
            changed.append(key)
        elif file_hash(src["path"]) != src["hash"]:
            if key == "facts" and os.path.isfile(src.get("snapshot", "")):
                before, now = fact_blocks(src["snapshot"]), fact_blocks(src["path"])
                used = evidence_dependencies(state)
                if used and all(before.get(i) == now.get(i) for i in used):
                    continue
            changed.append(key)
    if "ad_files" in state:
        current = []
        ad = os.path.join(paths.job_dir(state["job"]), "ad")
        for folder, _, names in os.walk(ad):
            current.extend(os.path.relpath(os.path.join(folder, n), ad) for n in names)
        if sorted(current) != state["ad_files"]:
            changed.append("job pack")
    current_cv = state.get("current_cv")
    if current_cv and (not os.path.isfile(current_cv["path"]) or file_hash(current_cv["path"]) != current_cv["hash"]):
        changed.append("current CV")
    return changed


def fact_ids(path):
    with open(path, encoding="utf-8-sig") as f:
        ids = re.findall(r"^id:\s*(\S+)\s*$", f.read(), re.M)
    if len(ids) != len(set(ids)):
        raise ValueError("The evidence ledger contains duplicate ids; resolve them before rewriting.")
    return set(ids)


def evidence_ids(path):
    ids = fact_ids(path)
    with open(path, encoding="utf-8-sig") as f:
        for block in re.findall(r"```(.*?)```", f.read(), re.S):
            ident = re.search(r"^id:\s*(\S+)\s*$", block, re.M)
            if ident and re.search(r"^conflict:\s*true\s*$", block, re.M | re.I):
                ids.discard(ident[1])
    return ids


def evidence_excerpts(path, wanted):
    with open(path, encoding="utf-8-sig") as f:
        text = f.read()
    result = {}
    for block in re.findall(r"```(.*?)```", text, re.S):
        ident = re.search(r"^id:\s*(\S+)\s*$", block, re.M)
        if not ident or ident[1] not in wanted:
            continue
        values = [v.strip().strip('"') for v in re.findall(r"^\s*text:\s*(.+)$", block, re.M)]
        context = [v.strip().strip('"') for v in re.findall(r"^\s*(?:title|employer|section|cv|display_dates|stated):\s*(.+)$", block, re.M)]
        result[ident[1]] = {"text": values, "context": context}
    return result


def require_refs(refs, known, label, source="facts.md"):
    if not isinstance(refs, list) or not refs or any(not isinstance(x, str) or x not in known for x in refs):
        if source == "asks.md":
            if not known:
                raise ValueError("brief.priorities needs requirement IDs, but none were found in this job's asks.md. Record the assessed job requirements there before preparing the writing brief.")
            example = json.dumps(sorted(known)[:2])
            raise ValueError("brief.priorities must be a non-empty JSON array of existing requirement IDs from this job's asks.md, for example %s. Use IDs only, not requirement descriptions, objects or CV fact IDs. Supporting CV evidence belongs in pillar/section facts and sample claims, not in priorities." % example)
        raise ValueError("%s needs existing evidence ids, with none missing or invented." % label)


def validate_brief(brief, sources):
    if not isinstance(brief, dict):
        raise ValueError("The application brief must be an object.")
    facts = evidence_ids(sources["facts"]["path"])
    asks = fact_ids(sources["asks"]["path"])
    for key in ("target", "central_case", "voice", "boundaries", "section_plan", "constraints"):
        if not brief.get(key):
            raise ValueError("The application brief needs %s." % key)
    for key in ("target", "central_case", "voice"):
        if not isinstance(brief[key], str):
            raise ValueError("The brief's %s must be text." % key)
    if not isinstance(brief["constraints"], dict):
        raise ValueError("Record application limits and budgets in a constraints object.")
    require_refs(brief.get("priorities"), asks, "brief.priorities", source="asks.md")
    pillars = brief.get("pillars", {})
    for key in PILLARS:
        p = pillars.get(key, {})
        if p.get("status") not in ("supported", "absent"):
            raise ValueError("Record %s as supported or absent; uncertainty is not a printed claim." % key)
        if not norm(p.get("statement")):
            raise ValueError("Explain the evidence or absence of %s." % key)
        if p["status"] == "supported":
            require_refs(p.get("facts"), facts, key)
        elif p.get("facts"):
            raise ValueError("An absent pillar must not claim supporting evidence.")
    if not isinstance(brief["section_plan"], list):
        raise ValueError("The section plan is a list of section, purpose and evidence choices.")
    for section in brief["section_plan"]:
        if not isinstance(section, dict) or not section.get("section") or not section.get("purpose"):
            raise ValueError("Each planned section needs its name and purpose.")
        if section.get("facts"):
            require_refs(section["facts"], facts, "The section plan")


def claims_valid(suggested, claims, facts):
    if not isinstance(claims, list) or not claims:
        raise ValueError("Each suggested passage needs a claim-to-evidence map.")
    for claim in claims:
        if not isinstance(claim, dict):
            raise ValueError("Each claim must contain exact text and its fact ids.")
        require_refs(claim.get("facts"), facts, "Each claim")
        if not norm(claim.get("text")):
            raise ValueError("A claim needs the exact text it supports.")
    if norm(" ".join(c["text"] for c in claims)) != norm(suggested):
        raise ValueError("The claim map must cover the full suggested text in order. Review the meaning against the cited sources too.")


def source_lines(path):
    import assemble
    with open(path, encoding="utf-8-sig") as f:
        scanned = assemble.scan(f.read())
    units = [u for u in scanned["units"] if u["id"]]
    known = {u["id"]: u["text"] for u in units}
    if len(known) != len(units):
        raise ValueError("This source has ambiguous duplicate section/line ids. Resolve the heading structure visibly before preparing the rewrite.")
    for section in scanned["sections"]:
        for role in section["roles"]:
            if role["dates_in_head"]:
                known[role["base"] + "/d"] = role["dates"]
    return known


def validate_samples(samples, sources, available):
    if not isinstance(samples, list) or not samples:
        raise ValueError("Prepare at least one writing sample from this CV before asking for a mode choice.")
    known = source_lines(sources["cv"]["path"])
    facts = evidence_ids(sources["facts"]["path"])
    seen = set()
    wording = {}
    for sample in samples:
        if not isinstance(sample, dict):
            raise ValueError("Each sample must contain a mode, profile and bullet.")
        mid = sample.get("mode")
        if mid not in available or mid in seen:
            raise ValueError("Each sample needs a different available writing mode.")
        seen.add(mid)
        sample["definition"] = copy.deepcopy(available[mid])
        for key in ("profile", "bullet"):
            p = sample.get(key, {})
            ids = p.get("lines", [p.get("line")])
            if not isinstance(ids, list) or not ids or any(not isinstance(i, str) for i in ids) or len(set(ids)) != len(ids):
                raise ValueError("Each sample needs distinct source line IDs in source order.")
            current = " ".join(known.get(i, "") for i in ids)
            new_profile = key == "profile" and ids == ["new:profile"]
            if not new_profile and (any(i not in known for i in ids) or norm(p.get("current")) != norm(current)):
                raise ValueError("The %s sample must quote its source lines exactly." % key)
            if new_profile and p.get("current"):
                raise ValueError("A new profile has no current text to quote.")
            if new_profile and any(re.search(r"(^|-)(profile|summary)(-|$)", i.split("/")[0]) for i in known):
                raise ValueError("This CV already has a profile or summary. Quote the complete source profile instead of claiming it is missing.")
            if key == "profile" and not new_profile:
                section = ids[0].split("/")[0]
                full = [i for i in known if i.startswith(section + "/")]
                if ids != full or any(i.count("/") != 1 for i in ids):
                    raise ValueError("Quote the complete source profile in source order using lines, not one paragraph labelled as the profile summary.")
                # Preserve paragraph/bullet boundaries in the original displayed by
                # every mode; the agent cannot truncate the source card for space.
                p["current"] = "\n\n".join(known[i] for i in ids)
            p["preview_only"] = True
            claims_valid(p.get("suggested", ""), p.get("claims"), facts)
        if not sample.get("why"):
            raise ValueError("Explain what each mode's samples emphasise.")
        pair = tuple(norm(sample[k]["suggested"]).casefold() for k in ("profile", "bullet"))
        if pair in wording:
            raise ValueError("Modes %s and %s have identical samples. Demonstrate a meaningful difference or offer fewer distinct choices; never invent facts to create contrast." % (wording[pair], mid))
        wording[pair] = mid
    anchors = [([s["profile"].get("lines", [s["profile"].get("line")]),
                 s["bullet"].get("lines", [s["bullet"].get("line")])]) for s in samples]
    if any(a != anchors[0] for a in anchors):
        raise ValueError("Compare modes on the same source profile and experience bullet.")


def prepare(job, cv, data):
    job = paths.find_job(job)
    data = copy.deepcopy(data)
    old = load(job) or {}
    old_options = {s["mode"]: s["definition"] for s in old.get("samples", [])}
    custom = data.get("custom_modes", [])
    slot = old.get("custom_slot") or next((s["mode"] for s in reversed(old.get("samples", [])) if s["mode"].startswith("personal-")), None)
    replace = old.get("request", {}).get("replace_mode") or slot
    keep_custom = data.get("keep_custom_modes", old.get("request", {}).get("keep_custom_modes", False))
    if custom and replace in old_options and not keep_custom:
        incoming = next((m for m in custom if m["id"] == data.get("preview_mode")), custom[-1])
        incoming_id = incoming["id"]
        previous = old_options[replace]
        changed = {k:v for k,v in incoming.items() if k not in ("id", "version")} != {k:v for k,v in previous.items() if k not in ("id", "version")}
        incoming["id"] = replace
        latest = max([previous["version"]] + [m["version"] for m in modes() if m["id"] == replace])
        incoming["version"] = latest + 1 if changed else previous["version"]
        data["custom_modes"] = [m for m in custom if m is incoming or m["id"] != replace]
        data["samples"] = [s for s in data.get("samples", []) if s["mode"] != replace or s["mode"] == incoming_id]
        for sample in data["samples"]:
            if sample["mode"] == incoming_id:
                sample["mode"] = replace
        data["preview_mode"] = replace
        slot = replace
    elif custom:
        slot = data.get("preview_mode") or custom[-1]["id"]
    sources = source_record(cv, job)
    brief, samples = data.get("brief", {}), copy.deepcopy(data.get("samples"))
    validate_brief(brief, sources)
    available = {m["id"]: m for m in modes()}
    available.update(old_options)
    for mode in data.get("custom_modes", []):
        validate_mode(mode)
        if not mode["id"].startswith("personal-"):
            raise ValueError("An exploratory mode needs a personal- id.")
        available[mode["id"]] = mode
    validate_samples(samples, sources, available)
    preview_mode = data.get("preview_mode")
    if preview_mode is not None and preview_mode not in {s["mode"] for s in samples}:
        raise ValueError("The preview mode must have samples in this comparison.")
    if old.get("phase") in ("rewrite_requested", "revision_requested") and not stale(old):
        raise ValueError("A rewrite request is pending. Publish its suggestions before preparing a different direction.")
    if old.get("request", {}).get("action") == "preview" and old["request"].get("save_as") and preview_mode and preview_mode.startswith("personal-"):
        save_mode(available[preview_mode])
    state = {"schema": 1, "job": job, "sources": sources, "brief": brief,
             "ad_files": sorted(key[3:] for key in sources if key.startswith("ad:")),
             "samples": samples, "phase": "choose", "selected": None,
             "preview_mode": preview_mode,
             "preview_base": old.get("request", {}).get("mode") if preview_mode else None,
             "custom_slot": slot,
             "handled_requests": old.get("handled_requests", []),
             "previous": old.get("revision"), "batches": old.get("batches", [])}
    # Exploration changes the offered direction, not the reviewed wording or its
    # active round. Preserve decisions only against the same exact CV source.
    for key in ("batch", "working_review", "review_seed"):
        if key in old:
            state[key] = copy.deepcopy(old[key])
    if old.get("current_cv", {}).get("hash") == sources["cv"]["hash"]:
        state["working_review"] = old.get("working_review", {})
    # The archived state retains every older sample and decision. Preparation never
    # changes the CV and never turns the default into the user's selection.
    return save(job, state)


def parse_handoff(path):
    with open(path, encoding="utf-8-sig") as f:
        text = f.read()
    try:
        value = json.loads(text)
    except ValueError:
        match = re.search(r"```json\s*(\{.*\})\s*```", text, re.S)
        if not match:
            raise ValueError("Save the writing request or the complete hand-to-AI block, including its JSON.")
        value = json.loads(match.group(1))
    return value


def request(job, data):
    job = paths.find_job(job)
    state = load(job)
    req = data.get("writing_request", data)
    if not state or req.get("job") != job or req.get("schema") != 1:
        raise ValueError("This writing request does not belong to the prepared application.")
    rid = req.get("id")
    if not isinstance(rid, str) or not rid:
        raise ValueError("The writing request needs its own id.")
    if rid in state.get("handled_requests", []):
        return state
    if req.get("revision") != state["revision"] or stale(state):
        raise ValueError("The application changed after these samples were shown. Refresh the Studio before choosing the new direction.")
    action = req.get("action")
    if action not in ("rewrite", "preview", "revise"):
        raise ValueError("A writing request must ask for samples, a rewrite or a revision.")
    req = copy.deepcopy(req)
    expected_scope = "lines" if action == "revise" else "preference" if action == "preview" and req.get("save_as") else "application"
    if req.get("scope", expected_scope) != expected_scope:
        raise ValueError("Local revisions, application previews and saved preferences must keep their distinct scopes.")
    req["scope"] = expected_scope
    options = {s["mode"]: s for s in state["samples"]}
    if req.get("mode") not in options:
        raise ValueError("Choose a mode whose samples are on this application.")
    definition = options[req["mode"]]["definition"]
    for field, key in (("mode_name", "name"), ("mode_version", "version")):
        if field in req and req[field] != definition[key]:
            raise ValueError("The request's mode name or version does not match its prepared mode. Recreate the handoff from the current Studio so the displayed choice and recorded direction agree.")
        # Older handoffs carry only the ID; resolve the label from the prepared
        # snapshot, never from a newer global mode or an inferred display name.
        req[field] = definition[key]
    expected_source = state.get("current_cv", state["sources"]["cv"])
    if req.get("source_hash") != expected_source["hash"]:
        raise ValueError("The writing request must refer to the current CV shown in the Studio.")
    memory.capture(state, data, expected_source["hash"])
    if state.get("current_cv"):
        state["sources"]["cv"] = copy.deepcopy(state.pop("current_cv"))
    if action == "preview" and not req.get("keep_custom_modes", False):
        req["replace_mode"] = req["mode"] if req["mode"].startswith("personal-") else state.get("custom_slot")
    if action == "revise" and not state.get("selected"):
        raise ValueError("Choose the writing direction before requesting a revision.")
    if action == "revise" and req["mode"] != state["selected"]["id"]:
        raise ValueError("Preview a different mode before asking it to replace the current direction.")
    if action in ("rewrite", "revise") and req.get("adjustments", "").strip() and action == "rewrite":
        raise ValueError("Preview your adjusted direction first so the full rewrite follows the samples you chose.")
    state["request"] = copy.deepcopy(req)
    if data.get("marks") is not None:
        state["request"]["decisions"] = {k: v for k, v in data.items() if k != "writing_request"}
    state["revision_context"] = {"scope": expected_scope, "request": rid,
        "brief": digest(state["brief"]), "source": state["sources"]["cv"]["hash"],
        "feedback": req.get("adjustments", "")}
    state.setdefault("handled_requests", []).append(rid)
    state["phase"] = {"rewrite": "rewrite_requested", "preview": "preview_requested", "revise": "revision_requested"}[action]
    if action != "preview":
        state["selected"] = copy.deepcopy(options[req["mode"]]["definition"])
    prior = batch_for(state)
    state["transition"] = {"from_batch": prior["id"] if prior else None,
                           "mode": definition["name"], "generation_required": action != "preview",
                           "reused": False, "preserve_user_wording": True}
    if action == "rewrite" and not req.get("force_regenerate"):
        cached = memory.reusable(state, definition)
        if cached:
            state["batch"] = cached["id"]
            state["phase"] = "review"
            memory.seed(state, cached)
            state["transition"].update(generation_required=False, reused=True)
    return save(job, state)


def review_valid(review):
    for key in OBJECTIVES:
        item = review.get(key, {})
        if item.get("status") not in ("pass", "needs_attention") or not norm(item.get("notes")):
            raise ValueError("Record a substantive %s review with status and notes." % key)


def validate_profile_structure(records, state):
    """Check the actual proposed profile, not a claimed paragraph count in review.

    Untouched source text and the person's later accept/reject decisions remain
    theirs. This gate applies to generated profile changes, never voice previews.
    Semantic richness still requires reading the complete source and draft.
    """
    import assemble
    with open(state["sources"]["cv"]["path"], encoding="utf-8-sig") as f:
        source = f.read()
    source_scan = assemble.scan(source)
    sections = {s["sid"] for s in source_scan["sections"]
                if re.search(r"\b(profile|summary)\b", s["title"], re.I)}
    for sample in state.get("samples", []):
        passage = sample["profile"]
        ids = passage.get("lines", [passage.get("line")])
        if ids != ["new:profile"]:
            sections.add(ids[0].split("/")[0])
    for rec in records:
        spec = rec.get("section", {})
        if spec and re.search(r"\b(profile|summary)\b", spec.get("title", ""), re.I):
            sections.add(spec["slug"])
    decisions = {"marks": {}, "adds": {}, "sections": []}
    changed = set()
    for rec in records:
        kind, line = rec["kind"], rec.get("line", "")
        if kind == "section" and rec["section"]["slug"] in sections:
            decisions["sections"].append(rec["section"])
            changed.add(rec["section"]["slug"])
        elif line.split("/")[0] in sections and kind in ("edit", "remove", "add"):
            changed.add(line.split("/")[0])
            if kind == "add":
                decisions["adds"].setdefault(line.split("/+")[0], []).append({"text": rec["sug"]})
            else:
                decisions["marks"][line] = {"a": kind, "text": rec.get("sug", "")}
    if not changed:
        return
    draft, _ = assemble.assemble(source, decisions)
    scanned = assemble.scan(draft)
    for sid in changed:
        units = [u for u in scanned["units"] if u["id"].startswith(sid + "/")]
        paragraphs = [u for u in units if u["kind"] == "para" and norm(u["text"])]
        if len(paragraphs) < 4:
            raise ValueError("The proposed full profile must contain at least four substantive paragraphs. "
                             "A condensed voice preview is not a replacement. Preserve breadth, pillars, "
                             "distinctive contribution and proof; do not pad or invent evidence.")


def publish(job, proposals, review):
    import proposal_records
    state = load(job)
    if not state or state["phase"] not in ("rewrite_requested", "revision_requested"):
        raise ValueError("There is no authorised rewrite request waiting for suggestions.")
    if stale(state):
        raise ValueError("The source evidence changed during rewriting. Refresh the application direction first.")
    # Unrelated additions to the shared record do not invalidate this application.
    # Snapshot the current ledger before proposals can cite newly added facts.
    state["sources"]["facts"] = source_record(state["sources"]["cv"]["path"], job)["facts"]
    review_valid(review)
    if any(review[k]["status"] != "pass" for k in OBJECTIVES):
        raise ValueError("Resolve the draft review findings before publishing suggestions.")
    with open(proposals, encoding="utf-8-sig") as f:
        text = f.read()
    records = proposal_records.parse(text)
    reuse = review.get("reuse_proposals", [])
    if reuse:
        prior_id = state.get("transition", {}).get("from_batch")
        prior = next((b for b in state.get("batches", []) if b["id"] == prior_id), None)
        if not prior or prior["source"]["hash"] != state["sources"]["cv"]["hash"]:
            raise ValueError("Only reuse proposals from the previous round on this same source CV.")
        by_uid = {r["uid"]:r for r in prior["records"]}
        if not isinstance(reuse, list) or len(set(reuse)) != len(reuse) or any(uid not in by_uid for uid in reuse):
            raise ValueError("reuse_proposals must list distinct suggestion UIDs from the previous round.")
        records.extend(copy.deepcopy(by_uid[uid]) for uid in reuse)
        for i, rec in enumerate(records, 1):
            rec["p"] = "P%d" % i
    faults = proposal_records.validate(records, state["sources"]["cv"]["path"],
                                       state["sources"]["facts"]["path"],
                                       state["sources"]["asks"]["path"], strict=True)
    if faults:
        raise ValueError("\n".join(faults))
    validate_profile_structure(records, state)
    context = digest([state["sources"]["cv"]["hash"], state["selected"]])
    for record in records:
        record["uid"] = proposal_records.identity(record, context)
    batch = {"id": uuid.uuid4().hex, "source": copy.deepcopy(state["sources"]["cv"]),
             "sources": copy.deepcopy(state["sources"]),
             "mode": copy.deepcopy(state["selected"]), "brief": digest(state["brief"]),
             "request": state["request"]["id"], "review": review, "records": records,
             "text": text, "decisions": None}
    state.setdefault("batches", []).append(batch)
    state["batch"] = batch["id"]
    state["phase"] = "review"
    memory.seed(state, batch)
    return save(job, state)


def batch_for(state):
    return next((b for b in reversed(state.get("batches", [])) if b["id"] == state.get("batch")), None)


def decision_faults(data, state, cv=None, partial=False):
    if stale(state):
        return ["The writing evidence changed. Reconsider the affected brief and suggestions before applying decisions."]
    stamp = data.get("writing")
    if not stamp:
        return ["The decisions are missing their writing version. Export them from this application's Studio."]
    batch = batch_for(state)
    if not batch or stamp.get("job") != state["job"] or stamp.get("batch") != batch["id"]:
        return ["These decisions belong to a different application or suggestion version."]
    if cv and file_hash(cv) != batch["source"]["hash"]:
        return ["The CV changed after these suggestions were reviewed. Rebuild before applying the decisions."]
    if stamp.get("source_hash") != batch["source"]["hash"]:
        return ["These decisions refer to a different source CV version."]
    if data.get("undecided") and not partial:
        return ["Some suggestions are still undecided. Return to those suggestions before finishing the CV."]
    expected = {r["uid"]: r for r in batch["records"]}
    found = set()
    faults = []
    for rec in data.get("proposals", []):
        uid = rec.get("uid")
        if uid not in expected or rec.get("suggested", "") != expected[uid].get("sug", ""):
            faults.append("A decision does not match the exact suggestion that was published.")
        else:
            if uid in found:
                faults.append("A suggestion decision appears twice.")
            found.add(uid)
        if rec.get("was") not in ("used", "kept", "edited", "removed", "answered", "nothing", "another"):
            faults.append("A suggestion has no recognised decision.")
        if rec.get("was") in ("another", "answered") and not partial:
            faults.append("A requested alternative is still waiting for its rewrite.")
        original = expected.get(uid, {})
        if rec.get("was") == "used":
            line = original.get("line", "")
            kind = original.get("kind")
            mark = data.get("marks", {}).get(line, {})
            if kind == "edit" and (mark.get("a") != "edit" or mark.get("text") != original.get("sug")):
                faults.append("An accepted rewrite does not match the text being applied.")
            if kind == "remove" and mark.get("a") != "remove":
                faults.append("An accepted removal is missing from the decisions.")
            if kind == "add" and not any(x.get("text") == original.get("sug") for x in data.get("adds", {}).get(line.split("/+")[0], [])):
                faults.append("An accepted addition is missing from the decisions.")
            ordering = data.get("section_order") if line == "document/sections" else data.get("order", {}).get(line)
            if kind == "order" and ordering != original.get("order"):
                faults.append("An accepted order is missing from the decisions.")
            if kind == "section" and not any(s.get("slug") == original["section"]["slug"] and
                    [x.get("text") for x in s.get("lines", [])] == [x.get("text") for x in original["section"]["lines"]]
                    for s in data.get("sections", [])):
                faults.append("An accepted section is missing or has changed text.")
    if not partial and found != set(expected):
        faults.append("The handoff must account for every published suggestion, including rejected ones.")
    return faults


def finish(job, cv, review, decisions):
    state = load(job)
    if not state:
        raise ValueError("Prepare this application's writing direction first.")
    review_valid(review)
    faults = decision_faults(decisions, state)
    if faults:
        raise ValueError("\n".join(faults))
    import render_cv
    import assemble
    with open(cv, encoding="utf-8-sig") as f:
        assembled = f.read()
        if any(render_cv.effect(decisions).values()) and not render_cv.baked_entry(assembled, decisions):
            raise ValueError("Finish requires the CV assembled from these exact decisions.")
    with open(batch_for(state)["source"].get("snapshot", batch_for(state)["source"]["path"]), encoding="utf-8-sig") as f:
        mismatch = assemble.verify(f.read(), decisions, assembled)
    if mismatch:
        raise ValueError("The assembled CV differs from the approved decisions: %s" % mismatch)
    batch_for(state)["decisions"] = copy.deepcopy(decisions)
    batch_for(state)["working_decisions"] = copy.deepcopy(decisions)
    state["final_review"] = review
    state["current_cv"] = source_record(cv, job)["cv"]
    state["phase"] = "ready" if all(review[k]["status"] == "pass" for k in OBJECTIVES) else "review_required"
    return save(job, state)


def page_data(job, cv=None):
    state = load(job)
    if not state:
        return {"schema": 1, "job": paths.find_job(job), "phase": "unprepared", "modes": modes()}
    out = copy.deepcopy(state)
    changed = stale(state)
    if cv:
        expected = state.get("current_cv", state["sources"]["cv"])
        if file_hash(cv) != expected["hash"]:
            changed.append("displayed CV")
    if changed:
        out["phase"] = "stale"
        out["changed"] = changed
    out["label"] = PHASES.get(out["phase"], out["phase"])
    # Full history remains on disk. The page only needs the active round.
    batch = batch_for(state)
    out["active_batch"] = batch
    if batch and batch["source"]["hash"] != out["sources"]["cv"]["hash"]:
        out["active_batch"] = None
    if out.get("review_seed", {}).get("source_hash") != file_hash(cv or state["sources"]["cv"]["path"]):
        out.pop("review_seed", None)
    out["history"] = memory.history(state)
    # Older jobs may have sampled only a middle profile paragraph. Rebuilding the
    # view must show the complete original from its saved source without changing
    # the saved comparison, selected mode, proposals, or decisions.
    source = state["sources"]["cv"]
    source_path = source.get("snapshot", source["path"])
    if os.path.isfile(source_path) and file_hash(source_path) == source["hash"]:
        known = source_lines(source_path)
        for sample in out.get("samples", []):
            profile = sample["profile"]
            ids = profile.get("lines", [profile.get("line")])
            if ids and ids[0] in known:
                section = ids[0].split("/")[0]
                full = [i for i in known if i.startswith(section + "/")]
                if all(i.count("/") == 1 for i in full):
                    profile["current"] = "\n\n".join(known[i] for i in full)
                    profile["lines"] = full
    facts = state["sources"]["facts"]
    evidence_path = facts.get("snapshot", facts["path"])
    out["evidence"] = evidence_excerpts(evidence_path, evidence_dependencies(state)) if os.path.isfile(evidence_path) else {}
    out["display_is_source"] = not cv or file_hash(cv) == state["sources"]["cv"]["hash"]
    out.pop("batches", None)
    out.pop("handled_requests", None)
    return out


def summary(job):
    state = load(job)
    if not state:
        return None
    phase = "stale" if stale(state) else state["phase"]
    return {"phase": phase, "next": PHASES.get(phase, phase),
            "mode": (state.get("selected") or {}).get("name", "Not selected"),
            "revision": state["revision"]}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)
    sub.add_parser("modes")
    sm = sub.add_parser("save-mode"); sm.add_argument("file")
    for command in ("prepare", "request", "publish", "finish", "context", "history"):
        p = sub.add_parser(command); p.add_argument("--job", required=True)
        if command in ("prepare", "finish"):
            p.add_argument("--cv", required=True)
        if command in ("prepare", "request", "publish", "finish"):
            p.add_argument("--input", required=True)
        if command == "publish":
            p.add_argument("--proposals", required=True)
        if command == "finish":
            p.add_argument("--decisions", required=True)
        if command == "context":
            p.add_argument("--batch", help="Read one saved round by ID instead of the current context")
    a = ap.parse_args(argv)
    try:
        if a.command == "modes":
            result = modes()
        elif a.command == "save-mode":
            result = {"saved": save_mode(read_json(a.file))}
        elif a.command == "context":
            state = load(a.job)
            if a.batch:
                result = next((b for b in (state or {}).get("batches", []) if b["id"] == a.batch), None)
                if result is None:
                    raise ValueError("That saved round does not exist in this job.")
            else:
                result = memory.context(state) if state else page_data(a.job)
        elif a.command == "history":
            result = memory.history(load(a.job) or {})
        elif a.command == "prepare":
            result = prepare(a.job, a.cv, read_json(a.input))
        elif a.command == "request":
            result = request(a.job, parse_handoff(a.input))
        elif a.command == "publish":
            result = publish(a.job, a.proposals, read_json(a.input))
        else:
            result = finish(a.job, a.cv, read_json(a.input), read_json(a.decisions))
        if a.command in ("prepare", "request", "publish", "finish"):
            result = memory.context(result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, KeyError, TypeError, OSError, paths.NoSuchJob) as exc:
        sys.stderr.write("Writing: %s\n" % exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
