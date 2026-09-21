#!/usr/bin/env python3
"""Refuse the faults that are silent otherwise.

    python3 check.py                    the person's own folder, from paths.py
    python3 check.py <folder>           somewhere else
    python3 check.py <folder> tight     only cv-tight.md, not every variant
    python3 check.py --job <id> [variant]   one job's folder

Checks the things that look fine on screen and are wrong on the page: a proposal
that traces to nothing, a claim printed twice, a budget quietly exceeded, a role
left in present tense after its end date, a banned construction, an invented figure.

The folder is the one holding `facts.md`, `asks.md`, `proposals.md` and the
`cv-*.md` drafts. With no argument that is the folder `scripts/paths.py` resolves,
which is where the ledgers actually live, so the documented command needs nothing
typed after it.

Standard library only.

    0   nothing found
    1   faults found
    2   the command line was wrong
    3   the folder is not there
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

NO_FOLDER = 3

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

# A role that has not finished. Any of these words in the dates and the role is still
# running, whatever else is in there.
STILL_THERE = re.compile(r"\b(present|current|currently|now|ongoing|to date)\b", re.I)


def _is_date_line(text):
    """Is this line only dates? render_cv.py's own test, asked of render_cv.py.

    This check used to read the `###` heading and nothing else, so it only ever saw
    a role that had ended on a CV written `### Title | 2019 to 2023`. render_cv.py's
    parser exists partly because almost nobody writes it that way: the dates go on
    the line underneath. On the CV most people actually write, no role was ever seen
    as ended and the past tense check never fired once.

    The renderer is asked rather than copied, because a second copy of that test here
    would drift from the one that decides what prints.
    """
    try:
        import render_cv
        return render_cv._is_date_line(text)
    except Exception:                                          # noqa: BLE001
        return False


def role_dates(head, body_lines):
    """The dates of one `### role`, wherever this person put them.

    Three places, in the order render_cv.py looks: after a `|` in the heading, on the
    first line under the heading, and last the tail of the heading after a comma,
    which is the shape this check used to be built around.
    """
    if "|" in head:
        return head.rsplit("|", 1)[1].strip()
    for raw in body_lines:
        if not raw.strip():
            continue
        return raw.strip() if _is_date_line(raw.strip()) else ""
    return ""


def role_ended(head, body_lines):
    """Has this role finished? Unknown dates count as not finished.

    Erring towards no is deliberate: a wrong yes tells somebody their present tense
    is a fault on a job they still hold, and being told off for describing today's
    work in today's tense is how a person stops believing the rest of the output.
    """
    dates = role_dates(head, body_lines)
    if not dates:
        tail = head.rsplit(",", 1)[-1].strip()
        dates = tail if _is_date_line(tail) else ""
    if not dates or STILL_THERE.search(dates):
        return False
    return bool(re.search(r"(19|20)\d\d", dates))


def read(path):
    """The text of one file, whatever it was saved as.

    A CV that has been through Word on a Windows machine is often cp1252, and one
    curly apostrophe in it used to end the whole run with a UnicodeDecodeError
    partway through, having reported nothing about the files it had already read.
    Reading a CV is not the place to be strict about encodings.
    """
    with open(path, "rb") as f:
        raw = f.read()
    for enc in ("utf-8-sig", "utf-8", "cp1252"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1", "replace")


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
        body_lines = body.split("\n")
        if not role_ended(head, body_lines):
            continue
        for raw in body_lines:
            line = raw.strip().lstrip("-").strip()
            if not line or line.startswith("#") or _is_date_line(line):
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
        has_q = "**Question:**" in e
        if not has_current:
            faults.append("%s %s has no Currently block." % (name, pid))
        # An entry with no Suggested is not always malformed. rewriting.md says that
        # where the stronger line needs a fact nobody has, the correct output is the
        # question rather than the rewrite, and build_studio.py carries such an entry
        # into the studio as a question against its line. It still has to say what it
        # is asking, or the person is shown a card with nothing on it.
        if not has_sugg and not has_q:
            faults.append("%s %s has neither a Suggested block nor a Question block. "
                          "One of the two: the replacement wording, or the question "
                          "the wording is waiting on." % (name, pid))
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
            notes.append("%s %s adds a line without explaining the resulting length. Explain "
                         "growth; propose a tradeoff only under an explicit user/application limit." % (name, pid))
    return text


def _decisions_beside(root, cv):
    """The decisions file this draft belongs with, or None.

    The note the assembly leaves in the markdown names its own file, so that is asked
    first. Failing that, the two names the skill actually writes.
    """
    stem = cv[3:-3] if cv.startswith("cv-") and cv.endswith(".md") else cv
    tries = []
    try:
        import render_cv
        note = render_cv.read_note(read(os.path.join(root, cv)))
        for e in ((note or {}).get("baked") or []):
            if e.get("file"):
                tries.append(e["file"])
    except Exception:                                          # noqa: BLE001
        pass
    tries += ["cv-%s-decisions.json" % stem, "cv-decisions.json"]
    for fn in tries:
        if os.path.isfile(os.path.join(root, fn)):
            return fn
    return None


def check_pair(root, cv, faults, notes):
    """Does this markdown hold what the person decided, or only some of it?

    `cv-<variant>.md` is the deliverable and the master, which is only true when every
    removal, addition, rewrite, reordering and ticked section is actually in it. A
    markdown still holding a line the person took off is the fault this whole check
    exists for: the PDF looked right, so nobody ever opened the file they were pasting
    into the portal.
    """
    fn = _decisions_beside(root, cv)
    if not fn:
        return
    try:
        import json

        import assemble
        with open(os.path.join(root, fn), encoding="utf-8") as f:
            d = json.load(f)
    except ValueError as exc:
        faults.append("%s is not valid JSON: %s. Nothing can be checked against it, "
                      "and nothing can be assembled from it." % (fn, exc))
        return
    except Exception as exc:                                   # noqa: BLE001
        notes.append("%s could not be read as a decisions file (%s), so %s was not "
                     "checked against it." % (fn, exc, cv))
        return
    src = d.get("cv") if isinstance(d, dict) else None
    # The CV the decisions were made about is the source, and a source is supposed to
    # still hold every line somebody decided to take off. It is the variant written
    # from it that has to hold the decisions, so the source is never audited as one.
    if src and os.path.basename(src) == cv:
        return
    if src and not os.path.isfile(os.path.join(root, src)):
        src = None
    for msg in assemble.audit(read(os.path.join(root, cv)), d, cv_name=cv,
                              decisions_name=fn, source_name=src, folder=root):
        faults.append(msg)


def _default_root():
    """The person's own folder, or None when paths.py cannot be asked."""
    try:
        import paths
        return paths.data_dir()
    except Exception:
        return None


def _cv_files(root, variant):
    """The drafts to check. With a variant, only that one."""
    out = []
    for fn in sorted(os.listdir(root)):
        if not (fn.startswith("cv-") and fn.endswith(".md")):
            continue
        # The archive is a verbatim record of lines that came off a CV, not a draft.
        # Read as one it prints every rewrite twice, before and after, and the
        # same-claim-twice check fires on every one of them.
        if fn.endswith("-archive.md"):
            continue
        if variant:
            stem = fn[3:-3].lower()
            v = variant.lower()
            if stem != v and v not in stem:
                continue
        out.append(fn)
    return out


def _facts_for(root):
    """Only evidence prepared for this application; never discover older ledgers."""
    return os.path.join(root, "facts.md")


def main():
    argv = sys.argv[1:]
    if [a for a in argv if a in ("-h", "--help")]:
        sys.stdout.write(__doc__.split("Checks the things")[0])
        return 0
    job = None
    if "--job" in argv:
        i = argv.index("--job")
        if i + 1 >= len(argv):
            sys.stderr.write("check.py: --job needs a job id after it.\n")
            return 2
        job = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    args = [a for a in argv if not a.startswith("-")]
    if len(args) > (1 if job else 2):
        sys.stderr.write("usage: check.py [folder] [variant]   or   check.py --job <id> [variant]\n")
        return 2

    if job:
        try:
            import paths
            root = paths.job_dir(job)
        except Exception as e:                                 # noqa: BLE001
            sys.stderr.write("check.py: %s\n" % e)
            return NO_FOLDER
        args = [root] + args
    if args:
        root = os.path.abspath(os.path.expanduser(args[0]))
    else:
        root = _default_root()
        if root is None:
            sys.stderr.write(
                "check.py: no folder given and paths.py could not say where this "
                "person's folder is. Pass the folder, or --job <id>.\n")
            return 2
    variant = args[1] if len(args) > 1 else ""

    if not os.path.isdir(root):
        sys.stderr.write(
            "check.py: %s is not a folder, so there is nothing to check. This "
            "should be the folder holding facts.md, asks.md, proposals.md and the "
            "cv-*.md drafts. Run python3 scripts/paths.py to see where that is.\n"
            % root)
        return NO_FOLDER

    print("Checking %s%s" % (root, (", variant %s" % variant) if variant else ""))
    faults, notes = [], []

    facts_ids, ask_ids = set(), set()
    fp = _facts_for(root)
    if fp != os.path.join(root, "facts.md"):
        print("facts from %s" % fp)
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
        if not job and (os.path.isdir(os.path.join(root, "3 Jobs"))
                        or os.path.isdir(os.path.join(root, "jobs"))):
            notes.append("This is the person's folder, and each job's asks.md is in its "
                         "own folder now. Run check.py --job <id>.")

    pp = os.path.join(root, "proposals.md")
    if os.path.isfile(pp):
        check_proposals(pp, facts_ids, ask_ids, faults, notes)

    if job:
        import writing
        import proposal_records
        state = writing.load(job)
        if state:
            changed = writing.stale(state)
            if changed:
                faults.append("Writing inputs changed: %s. Refresh the brief and samples." % ", ".join(changed))
            batch = writing.batch_for(state)
            if batch and not changed:
                faults.extend(proposal_records.validate(batch["records"], batch["source"]["path"],
                    state["sources"]["facts"]["path"], state["sources"]["asks"]["path"], strict=True))

    cvs = _cv_files(root, variant)
    for fn in cvs:
        check_cv(os.path.join(root, fn), faults, notes)
        check_pair(root, fn, faults, notes)
    if variant and not cvs:
        notes.append("No cv-*.md matching %r in this folder." % variant)

    for fn in sorted(os.listdir(root)):
        if not fn.endswith(".md") or fn == "facts.md":
            continue
        # The archive quotes the person's own wording back at them, word for word.
        # Correcting a dash in a verbatim record would falsify the record, so the
        # archive is left out of this sweep and the fault is reported on the CV.
        if fn.endswith("-archive.md"):
            continue
        # A variant means this one draft, so the other drafts are not read at all.
        if variant and fn.startswith("cv-") and fn not in cvs:
            continue
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
