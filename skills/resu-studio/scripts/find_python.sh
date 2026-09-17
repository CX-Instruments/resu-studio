#!/bin/sh
# Find a Python 3 this skill can run with, on a Mac, Linux, or Git Bash on Windows, and
# print its full path.
#
#     sh scripts/find_python.sh
#
# The same job as find_python.ps1, for the shells that are not PowerShell. `python3` is
# usually right on a Mac or Linux, but not always: Anaconda and Miniconda often sit in
# ~/miniconda3 without being on the PATH of the shell an assistant opens, and in Git Bash
# on Windows `python3` is usually missing and `python` can be the Microsoft Store
# placeholder. So this tries everywhere Python is commonly installed, runs each one, and
# keeps the first that really is Python 3.8 or newer. The path is the last line printed.
#
# Remembered in <config>/python.txt (~/.resu-studio, or $RESU_STUDIO_CONFIG) and checked
# again before it is trusted. $RESU_PYTHON is tried first.
#
# Exit codes: 0 found, 1 no Python 3.8+ anywhere it looked.

config="${RESU_STUDIO_CONFIG:-$HOME/.resu-studio}"
cache="$config/python.txt"

check() {
    exe="$1"
    [ -n "$exe" ] || return 1
    [ -f "$exe" ] || exe=$(command -v "$exe" 2>/dev/null) || return 1
    [ -n "$exe" ] && [ -f "$exe" ] || return 1
    real=$("$exe" -c 'import sys
v = sys.version_info
print(sys.executable if v[0] == 3 and v[1] >= 8 else "")' 2>/dev/null) || return 1
    real=$(printf '%s' "$real" | tr -d '\r' | tail -n 1)
    [ -n "$real" ] || return 1
    mkdir -p "$config" 2>/dev/null && printf '%s\n' "$real" > "$cache" 2>/dev/null
    printf '%s\n' "$real"
    exit 0
}

[ -n "$RESU_PYTHON" ] && check "$RESU_PYTHON"
[ -f "$cache" ] && check "$(head -n 1 "$cache" | tr -d '\r')"
[ -n "$CONDA_PREFIX" ] && { check "$CONDA_PREFIX/bin/python"; check "$CONDA_PREFIX/python.exe"; }
[ -n "$CONDA_EXE" ] && { d=$(dirname "$(dirname "$CONDA_EXE")"); check "$d/bin/python"; check "$d/python.exe"; }

user_home="$HOME"
win_home=""
[ -n "$USERPROFILE" ] && command -v cygpath >/dev/null 2>&1 && win_home=$(cygpath -u "$USERPROFILE")
win_local=""
[ -n "$LOCALAPPDATA" ] && command -v cygpath >/dev/null 2>&1 && win_local=$(cygpath -u "$LOCALAPPDATA")

for root in "$user_home" "$win_home" "$win_local" /opt /usr/local /c /c/ProgramData /c/tools /d; do
    [ -n "$root" ] || continue
    for name in miniconda3 Miniconda3 anaconda3 Anaconda3 miniforge3 mambaforge miniconda anaconda; do
        check "$root/$name/bin/python"
        check "$root/$name/python.exe"
    done
done

check python3
check /opt/homebrew/bin/python3
check /usr/local/bin/python3
check /usr/bin/python3
if command -v py >/dev/null 2>&1; then
    p=$(py -3 -c 'import sys; print(sys.executable)' 2>/dev/null | tr -d '\r')
    [ -n "$p" ] && check "$(command -v cygpath >/dev/null 2>&1 && cygpath -u "$p" || printf '%s' "$p")"
fi
for d in "$win_local/Programs/Python"/Python3* /c/Program\ Files/Python3*; do
    [ -d "$d" ] && check "$d/python.exe"
done
check python

echo "resu-studio: no Python 3.8 or newer was found. Looked in the conda folders (miniconda3, anaconda3, miniforge3, mambaforge) under your home folder, /opt and /usr/local, Homebrew, the py launcher, python.org installs, and the PATH. If Python is installed somewhere else, set RESU_PYTHON to it." >&2
exit 1
