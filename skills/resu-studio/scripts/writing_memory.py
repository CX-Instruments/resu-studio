"""Saved review rounds and conservative reuse within one application's history.

No model call is needed to restore an unchanged round. Candidate wording stays
in the review overlay until explicitly accepted, including after a mode switch.
"""
import copy
import uuid


def capture(state, data, source_hash):
    import writing as W
    if "marks" not in data:
        return
    decisions = copy.deepcopy({k: v for k, v in data.items() if k != "writing_request"})
    batch = W.batch_for(state)
    if batch and batch["source"]["hash"] == source_hash:
        faults = W.decision_faults(decisions, state, partial=True)
        if faults:
            raise ValueError("Cannot preserve this review: " + " ".join(faults))
        batch["working_decisions"] = decisions
    elif decisions.get("proposals"):
        raise ValueError("These proposal decisions do not belong to the CV currently being shown.")
    state["working_review"] = {"source_hash": source_hash, "decisions": decisions}


def current_decisions(state):
    if state.get("working_review", {}).get("source_hash") == state["sources"]["cv"]["hash"]:
        return copy.deepcopy(state["working_review"]["decisions"])
    return {}


def reusable(state, definition):
    import writing as W
    for batch in reversed(state.get("batches", [])):
        if (batch["mode"] != definition or batch["brief"] != W.digest(state["brief"])
                or batch["source"]["hash"] != state["sources"]["cv"]["hash"]):
            continue
        if not source_matches(state, batch):
            continue
        decisions = batch.get("working_decisions") or batch.get("decisions") or {}
        if any(d.get("was") in ("another", "answered") for d in decisions.get("proposals", [])):
            continue
        return batch
    return None


def source_matches(state, batch):
    import writing as W
    # Unrelated ledger additions are allowed only when every cited fact is intact.
    prior = {"job": state["job"], "sources": batch["sources"],
             "brief": state["brief"], "samples": state["samples"],
             "batch": batch["id"], "batches": [batch],
             "ad_files": sorted(k[3:] for k in batch["sources"] if k.startswith("ad:"))}
    return batch["source"]["hash"] == state["sources"]["cv"]["hash"] and not W.stale(prior)


def content_key(record):
    import writing as W
    # Rationale and mode labels do not change the words a person approved.
    # Evidence, target, source wording and structural changes do.
    return W.digest({k: record.get(k) for k in
                     ("line", "kind", "cur", "sug", "claims", "draws", "order", "section", "q")})


def effect_matches(record, decision, data):
    kind, line, was = record["kind"], record["line"], decision.get("was")
    mark = data.get("marks", {}).get(line, {})
    if was == "used":
        if kind == "edit":
            return mark.get("a") == "edit" and mark.get("text") == record.get("sug")
        if kind == "remove":
            return mark.get("a") == "remove"
        if kind == "add":
            return any(x.get("text") == record.get("sug") for x in data.get("adds", {}).get(line.split("/+")[0], []))
        if kind == "order":
            return (data.get("section_order") if line == "document/sections" else data.get("order", {}).get(line)) == record.get("order")
        if kind == "section":
            return any(s.get("slug") == record["section"]["slug"] and
                       [x.get("text") for x in s.get("lines", [])] == [x.get("text") for x in record["section"]["lines"]]
                       for s in data.get("sections", []))
    if was == "edited":
        return bool(decision.get("text")) and mark.get("a") == "edit" and mark.get("text") == decision["text"]
    if was == "removed":
        return mark.get("a") == "remove"
    return was in ("kept", "nothing")


def seed(state, batch):
    """Keep current content; transfer only decisions on identical suggestions."""
    base = current_decisions(state)
    decisions = {}
    for previous in state.get("batches", []):
        if not source_matches(state, previous):
            continue
        source = previous.get("working_decisions") or previous.get("decisions") or {}
        by_uid = {r["uid"]: r for r in previous["records"]}
        for d in source.get("proposals", []):
            if d.get("uid") in by_uid:
                decisions[content_key(by_uid[d["uid"]])] = d
    # The incoming handoff is the latest user choice, regardless of round order.
    for d in base.get("proposals", []):
        for previous in state.get("batches", []):
            rec = next((r for r in previous["records"] if r["uid"] == d.get("uid")), None)
            if rec and source_matches(state, previous):
                decisions[content_key(rec)] = d
                break
    transferred = []
    for rec in batch["records"]:
        d = decisions.get(content_key(rec))
        if d and effect_matches(rec, d, base):
            transferred.append(dict(copy.deepcopy(d), uid=rec["uid"], p=rec["p"], line=rec["line"], suggested=rec.get("sug", "")))
    base["proposals"] = transferred
    base["writing"] = {"job": state["job"], "batch": batch["id"], "source_hash": batch["source"]["hash"]}
    decided = {d["uid"] for d in transferred}
    base["undecided"] = [{"p": r["p"], "line": r["line"], "kind": r["kind"]}
                         for r in batch["records"] if r["uid"] not in decided]
    batch["working_decisions"] = copy.deepcopy(base)
    state["working_review"] = {"source_hash": batch["source"]["hash"], "decisions": copy.deepcopy(base)}
    state["review_seed"] = {"token": uuid.uuid4().hex, "source_hash": batch["source"]["hash"], "decisions": base}


def history(state):
    return [{"batch": b["id"], "mode": b["mode"]["name"], "mode_id": b["mode"]["id"],
             "version": b["mode"]["version"], "suggestions": len(b["records"]),
             "decisions": len((b.get("working_decisions") or b.get("decisions") or {}).get("proposals", [])),
             "active": b["id"] == state.get("batch")}
            for b in state.get("batches", [])]


def context(state):
    import writing as W
    out = copy.deepcopy(state)
    out.pop("batches", None)
    out.pop("handled_requests", None)
    out.pop("review_seed", None)
    out["active_batch"] = copy.deepcopy(W.batch_for(state))
    out["history"] = history(state)
    return out
