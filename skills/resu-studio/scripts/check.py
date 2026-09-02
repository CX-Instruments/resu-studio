#!/usr/bin/env python3
"""Refuse the faults that are silent otherwise.

    python3 check.py <workbench-folder> [variant]

Checks the things that look fine on screen and are wrong on the page: a proposal
that traces to nothing, a claim printed twice, a budget quietly exceeded, a role
left in present tense after its end date, a banned construction, an invented figure.

Standard library only. Exit code 0 means nothing was found.
"""

import os
import re
import sys

BANNED_CHARS = {"—": "em dash", "–": "en dash"}

TRAITS = ("passionate", "proactive", "dynamic", "detail-oriented", "detail oriented",
          "results-driven", "results driven", "team player", "self-starter",
          "self starter", "hard-working", "go-getter")

SELF = ("i believe i am", "i would be a great", "my unique blend",
        "i am a fast learner", "i am the ideal candidate", "excellent fit")

# an intensifier is only a fault when no figure sits near it
INTENSIFIERS = ("dramatically", "significantly", "substantially", "greatly",
                "step-change", "step change")

FIGURE = re.compile(r"(\d[\d,.]*\s?(?:%|percent|hours?|days?|weeks?|months?|years?|"
                    r"staff|people|projects?|analysts?|agents?|sites?)|\$\s?\d)", re.I)

# A hedge that is always standing in for a smaller, truer verb. "Played a key role in"
# gets written when the honest word was "contributed to" and that felt too small. It
# is not too small, and a reader who has hired people can tell the difference.
HEDGES = ("was instrumental in", "played a key role in", "played a pivotal role",
          "was integral to", "helped to spearhead")

# Not wrong on sight, but almost always a plain verb wearing a costume. Flagged for a
# look rather than failed, because now and then one of them is the accurate word.
COSTUME_VERBS = ("spearheaded", "orchestrated", "championed", "leveraged",
                 "pioneered", "revolutionised", "revolutionized", "transformative")

PRESENT_VERBS = ("deliver ", "develop ", "build ", "perform ", "apply ", "automate ",
                 "manage ", "lead ", "support ", "maintain ", "coordinate ",
                 "liaise ", "oversee ", "design ", "conduct ", "currently ")


def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def check_dashes(name, text, faults):
    for ch, label in BANNED_CHARS.items():
        n = text.count(ch)
        if n:
            for i, line in enumerate(text.split("\n"), 1):
                if ch in line:
                    faults.append("%s line %d: %s. %s" % (name, i, label, line.strip()[:90]))
                    break
            if n > 1:
                faults.append("%s: %d more %s(s) in this file." % (name, n - 1, label))


def check_voice(name, text, faults, notes):
    low = text.lower()
    for t in TRAITS:
        if t in low:
            faults.append("%s uses the trait word %r. Unfalsifiable and on everybody's application." % (name, t))
    for s in SELF:
        if s in low:
            faults.append("%s assesses the person: %r. The reader decides that." % (name, s))
    for h in HEDGES:
        if h in low:
            faults.append("%s hedges a verb: %r. Say what they did. See references/rewriting.md."
                          % (name, h))
    for v in COSTUME_VERBS:
        if v in low:
            notes.append("%s: %r. Usually a plain verb in a costume, and often a bigger claim "
                         "than the record supports. Check it against the ledger."
                         % (name, v))
    for para in re.split(r"\n\s*\n", text):
        pl = para.lower()
        for w in INTENSIFIERS:
            if w in pl and not FIGURE.search(para):
                notes.append("%s: %r with no figure anywhere near it. Stronger without the word."
                             % (name, w))
                break


def parse_blocks(text):
    """Very small reader for the ``` fenced key: value blocks the templates use."""
    out = []
    for block in re.findall(r"```(.*?)```", text, re.S):
        d, key = {}, None
        for line in block.strip().split("\n"):
            m = re.match(r"^(\w[\w_]*):\s*(.*)$", line)
            if m:
                key = m.group(1)
                d[key] = m.group(2).strip()
            elif line.strip().startswith("-") and key:
                d.setdefault(key + "_list", []).append(line.strip()[1:].strip())
        if d:
            out.append(d)
    return out


def check_cv(path, faults, notes):
    text = read(path)
    name = os.path.basename(path)
    check_dashes(name, text, faults)
    check_voice(name, text, faults, notes)

    # a role with an end date must be entirely past tense
    roles = re.split(r"\n### ", text)
    for chunk in roles[1:]:
        head = chunk.split("\n", 1)[0]
        body = chunk.split("\n", 1)[1] if "\n" in chunk else ""
        ended = re.search(r"to\s+(19|20)\d\d\s*$", head.strip()) or "to 20" in head
        if not ended:
            continue
        for raw in body.split("\n"):
            line = raw.strip().lstrip("-").strip()
            if not line or line.startswith("#"):
                continue
            low = line.lower()
            for v in PRESENT_VERBS:
                if low.startswith(v):
                    faults.append("%s: %r has ended but a line starts in present tense: %r"
                                  % (name, head.strip()[:50], line[:70]))
                    break

    # the same claim printed twice
    lines = [l.strip().lstrip("-").strip() for l in text.split("\n")]
    lines = [l for l in lines if len(l.split()) >= 8 and not l.startswith("#")]
    seen = {}
    for l in lines:
        key = " ".join(norm(l).split()[:9])
        if key in seen:
            faults.append("%s prints the same claim twice: %r" % (name, l[:80]))
        seen[key] = 1

    # skills column width
    skills = re.search(r"## KEY SKILLS(.*?)(\n## |\Z)", text, re.S)
    if skills:
        groups = re.findall(r"^\*\*(.+?):\*\*", skills.group(1), re.M)
        if len(groups) > 9:
            notes.append("%s has %d skills groups. Past about nine this becomes a column "
                         "no layout can hold. Consider merging." % (name, len(groups)))
    return text


def _field(entry, label):
    """The text under **Label:** in one proposal entry, up to the next bold field."""
    m = re.search(r"\*\*%s:\*\*\s*(.*?)(?=\n\s*\*\*[A-Z][\w ]*:\*\*|\Z)"
                  % re.escape(label), entry, re.S)
    return " ".join(m.group(1).split()) if m else ""


def check_proposals(path, facts_ids, ask_ids, faults, notes):
    text = read(path)
    name = os.path.basename(path)
    check_dashes(name, text, faults)

    entries = re.split(r"\n## (?=P\d)", text)
    ids = {}
    for e in entries[1:]:
        pid = e.split(".", 1)[0].strip()
        if pid in ids:
            faults.append("%s: proposal id %s used twice." % (name, pid))
        ids[pid] = 1

        has_current = "**Currently:**" in e
        has_sugg = "**Suggested:**" in e
        if not has_current:
            faults.append("%s %s has no Currently block." % (name, pid))
        if not has_sugg:
            faults.append("%s %s has no Suggested block." % (name, pid))
        if "**Why:**" not in e:
            faults.append("%s %s has no reason. A change without one gets reversed by "
                          "the first person who disagrees." % (name, pid))
        if "Delete this" in e and "**Why:**" not in e:
            faults.append("%s %s deletes something with no reason." % (name, pid))

        for fid in re.findall(r"\*\*Draws on:\*\*\s*(.+)", e):
            for f in [x.strip() for x in fid.split(",") if x.strip()]:
                if facts_ids and f not in facts_ids:
                    faults.append("%s %s draws on %r, which is not in the facts ledger."
                                  % (name, pid, f))
        for aid in re.findall(r"\*\*Answers:\*\*\s*(.+)", e):
            for a in [x.strip() for x in aid.split(",") if x.strip()]:
                if ask_ids and a not in ask_ids:
                    faults.append("%s %s answers %r, which is not in this advertisement."
                                  % (name, pid, a))

        if "**Decision:**" not in e:
            notes.append("%s %s has no Decision line for the person to fill in." % (name, pid))

        if "**Line:**" not in e:
            faults.append("%s %s has no Line: id, so the studio cannot show it against "
                          "anything on the page and the person never sees it." % (name, pid))

        # A rewrite that halves a line has usually dropped a clause carrying a
        # constraint, a standard or a scale, and nobody can see what went.
        cur = _field(e, "Currently")
        sug = _field(e, "Suggested")
        if cur and sug and not cur.lower().startswith("not on the cv") \
                and not sug.lower().startswith("delete this"):
            cw, sw = len(cur.split()), len(sug.split())
            if cw >= 20 and sw < cw * 0.55:
                notes.append(
                    "%s %s cuts %d words to %d. Read both and name what is no longer "
                    "there. A condition, a standard, a scale or a stakeholder going "
                    "missing is an amputation, not a tightening, and if the cut is "
                    "right it should be proposed as a cut with its own reason."
                    % (name, pid, cw, sw))

    # additions must account for their cost
    for e in entries[1:]:
        if "Not on the CV" in e and "**Costs:**" not in e:
            pid = e.split(".", 1)[0].strip()
            notes.append("%s %s adds a line without saying what it costs. Name the removal "
                         "or say the budget rises." % (name, pid))
    return text


def main():
    if len(sys.argv) < 2:
        sys.stderr.write("usage: check.py <workbench-folder> [variant]\n")
        return 2
    root = os.path.abspath(os.path.expanduser(sys.argv[1]))
    faults, notes = [], []

    facts_ids, ask_ids = set(), set()
    fp = os.path.join(root, "facts.md")
    if os.path.isfile(fp):
        for b in parse_blocks(read(fp)):
            if b.get("id"):
                facts_ids.add(b["id"])
        conflicts = [b for b in parse_blocks(read(fp)) if b.get("conflict") == "true"]
        if conflicts:
            notes.append("facts.md: %d unresolved conflict(s) between CV variants. "
                         "These need the person, not a decision by you." % len(conflicts))
    else:
        notes.append("No facts.md. Phase 2 has not run.")

    ap = os.path.join(root, "asks.md")
    if os.path.isfile(ap):
        for b in parse_blocks(read(ap)):
            if b.get("id"):
                ask_ids.add(b["id"])
    else:
        notes.append("No asks.md. Phase 2 has not run.")

    pp = os.path.join(root, "proposals.md")
    if os.path.isfile(pp):
        check_proposals(pp, facts_ids, ask_ids, faults, notes)

    for fn in sorted(os.listdir(root)):
        if fn.startswith("cv-") and fn.endswith(".md"):
            check_cv(os.path.join(root, fn), faults, notes)

    for fn in sorted(os.listdir(root)):
        if fn.endswith(".md") and fn not in ("facts.md",):
            t = read(os.path.join(root, fn))
            check_dashes(fn, t, faults)

    print("facts: %d   asks: %d" % (len(facts_ids), len(ask_ids)))
    if notes:
        print("\nWorth looking at:")
        for n in dict.fromkeys(notes):
            print("  - " + n)
    if faults:
        print("\nFAILED, %d thing(s) to fix:" % len(dict.fromkeys(faults)))
        for f in dict.fromkeys(faults):
            print("  - " + f)
        return 1
    print("\nNothing found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
