"""Keep one version number, in SKILL.md, and copy it into every manifest.

The version lives in the skill's own frontmatter, under `metadata: version:`, because
SKILL.md is the one file every host installs. The Skills CLI, Gemini CLI and Copilot
copy only the skill folder, so a number kept anywhere else is not there to read.

    python3 tools/sync_version.py           copy it into every manifest
    python3 tools/sync_version.py --check   say what disagrees, change nothing

Also checks the frontmatter the way a strict installer reads it: that it parses at
all, that `name` matches the folder, and that `description` and `compatibility` are
inside the limits the Agent Skills standard sets. Exit 0 means all agree, 1 means
something needed changing (or would, with --check), 2 means the frontmatter is broken.

Standard library only, so it runs anywhere the skill does.
"""

import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_DIR = os.path.join(ROOT, "skills", "resu-studio")
SKILL_MD = os.path.join(SKILL_DIR, "SKILL.md")

#: Every manifest that carries a version, and where in it.
MANIFESTS = (
    (os.path.join(ROOT, ".claude-plugin", "plugin.json"), ("version",)),
    (os.path.join(ROOT, ".claude-plugin", "marketplace.json"), ("plugins", 0, "version")),
    (os.path.join(ROOT, ".codex-plugin", "plugin.json"), ("version",)),
)


def frontmatter():
    text = io.open(SKILL_MD, encoding="utf-8").read()
    m = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.S)
    if not m:
        raise ValueError("SKILL.md has no frontmatter")
    return m.group(1)


def problems_in(front):
    """What a strict YAML installer would trip on. Checked without a YAML library."""
    found = []
    fields = {}
    for line in front.splitlines():
        top = re.match(r"^([a-z][a-z-]*):\s?(.*)$", line)
        if top:
            fields[top.group(1)] = top.group(2)
            value = top.group(2)
            quoted = value[:1] in ("'", '"', "|", ">")
            if value and not quoted and (": " in value or " #" in value):
                found.append("%s holds ': ' or ' #' unquoted, which is not valid YAML "
                             "and makes a strict installer skip the skill" % top.group(1))
    if fields.get("name") != os.path.basename(SKILL_DIR):
        found.append("name is %r and the folder is %r; they must match"
                     % (fields.get("name"), os.path.basename(SKILL_DIR)))
    if not 1 <= len(fields.get("description", "")) <= 1024:
        found.append("description is %d characters; the limit is 1024"
                     % len(fields.get("description", "")))
    if len(fields.get("compatibility", "")) > 500:
        found.append("compatibility is %d characters; the limit is 500"
                     % len(fields["compatibility"]))
    return found


def skill_version(front):
    m = re.search(r"^\s+version:\s*[\"']?([0-9][^\"'\s]*)", front, re.M)
    if not m:
        raise ValueError("SKILL.md has no metadata: version:")
    return m.group(1)


def get_at(data, path):
    for key in path:
        data = data[key]
    return data


def set_at(data, path, value):
    for key in path[:-1]:
        data = data[key]
    data[path[-1]] = value


def main(argv):
    check = "--check" in argv
    try:
        front = frontmatter()
        broken = problems_in(front)
        version = skill_version(front)
    except (IOError, OSError, ValueError) as exc:
        print("sync_version: %s" % exc)
        return 2
    if broken:
        for b in broken:
            print("SKILL.md: %s" % b)
        return 2

    changed = 0
    for path, where in MANIFESTS:
        if not os.path.exists(path):
            continue
        data = json.load(io.open(path, encoding="utf-8"))
        have = get_at(data, where)
        if have == version:
            continue
        changed += 1
        rel = os.path.relpath(path, ROOT)
        if check:
            print("%s says %s; SKILL.md says %s" % (rel, have, version))
            continue
        set_at(data, where, version)
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        print("%s: %s -> %s" % (rel, have, version))

    if not changed:
        print("every manifest says %s, and SKILL.md's frontmatter is valid" % version)
    return 1 if changed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
