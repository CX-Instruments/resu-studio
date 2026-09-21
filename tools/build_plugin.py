"""Pack the plugin into dist/resu-studio-<version>.plugin, the file people upload to Claude.

A .plugin file is a zip. It holds the Claude manifest, the README, the CHANGELOG, the
public documentation linked by the README, and the whole skill folder. The version in the file name
comes from SKILL.md, so run tools/sync_version.py first; this refuses to build when a
manifest disagrees, because a file named 0.6.0 that says 0.5.0 inside helps nobody.

    python tools/build_plugin.py

Nothing a person keeps privately can end up inside: Python caches, a data folder and a
data-location.txt left in the skill folder are skipped. Standard library only.
"""

import os
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import sync_version  # noqa: E402

TOP_FILES = (".claude-plugin/plugin.json", "README.md", "CHANGELOG.md",
             "LICENSE", "PRIVACY.md", "TERMS.md", "docs/INSTALL.md")
README_IMAGES = ("writing.png", "writing-custom.png", "studio.png", "score.png",
                 "print.png", "desk.png")
SKIP_DIRS = {"__pycache__", "data"}
SKIP_FILES = {"data-location.txt", ".DS_Store", "Thumbs.db", "desk-updates.json"}


def skill_files():
    base = os.path.join(ROOT, "skills", "resu-studio")
    for folder, dirs, files in os.walk(base):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(files):
            if name in SKIP_FILES or name.endswith(".pyc"):
                continue
            full = os.path.join(folder, name)
            yield full, os.path.relpath(full, ROOT).replace(os.sep, "/")


def main():
    if sync_version.main(["--check"]) != 0:
        print("build_plugin: the version numbers disagree. Run python tools/sync_version.py, then build again.")
        return 1
    version = sync_version.skill_version(sync_version.frontmatter())
    out_dir = os.path.join(ROOT, "dist")
    out = os.path.join(out_dir, "resu-studio-%s.plugin" % version)
    if os.path.exists(out):
        print("build_plugin: %s already exists. Rename or move it first, so a released file "
              "is never replaced by accident." % os.path.relpath(out, ROOT))
        return 1
    os.makedirs(out_dir, exist_ok=True)
    count = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for rel in TOP_FILES:
            z.write(os.path.join(ROOT, rel), rel)
            count += 1
        for name in README_IMAGES:
            rel = "docs/images/" + name
            z.write(os.path.join(ROOT, rel), rel)
            count += 1
        for full, rel in skill_files():
            z.write(full, rel)
            count += 1
    print("wrote %s (%d files, %d KB)" % (os.path.relpath(out, ROOT), count, os.path.getsize(out) // 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
