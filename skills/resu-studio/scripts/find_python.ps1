# Find a Python 3 this skill can run with, on Windows, and print its full path.
#
#     powershell -NoProfile -ExecutionPolicy Bypass -File scripts\find_python.ps1
#
# Every other script in this folder is Python, so this one cannot be. On Windows the
# obvious commands often fail in ways that look like "Python is not installed":
#
#   - `python3` does not exist on most Windows machines.
#   - `python` can be the Microsoft Store placeholder in WindowsApps, which prints a
#     message or opens the Store instead of running anything.
#   - Anaconda and Miniconda do not put Python on the PATH unless you tick a box the
#     installer recommends against, so a perfectly good Python sits in
#     C:\Users\<you>\miniconda3\python.exe and nothing finds it.
#
# So this looks everywhere a Python is commonly installed, runs each one it finds, and
# keeps the first that really is Python 3.8 or newer. It prints that path on the last
# line and nothing else there, so an assistant can use it in every command as:
#
#     & "<the path>" scripts\paths.py --status
#
# The answer is remembered in <config>\python.txt (config is ~\.resu-studio, or
# $env:RESU_STUDIO_CONFIG) and checked again before it is trusted next time. Set
# $env:RESU_PYTHON to a python.exe to choose one yourself; it is tried first.
#
# Exit codes: 0 found, 1 no Python 3.8+ anywhere it looked.

$ErrorActionPreference = 'SilentlyContinue'

function Test-Python([string]$exe) {
    if (-not $exe) { return $null }
    if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) { return $null }
    # The Microsoft Store placeholder answers -c with an error and a non-zero exit code
    # instead of running anything, so it fails the test below like any broken Python.
    $out = & $exe -c "import sys; print('%d.%d' % sys.version_info[:2]); print(sys.executable)" 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $out) { return $null }
    $lines = @($out)
    if ($lines.Count -lt 2) { return $null }
    $ver = $lines[0].Trim().Split('.')
    if ([int]$ver[0] -ne 3 -or [int]$ver[1] -lt 8) { return $null }
    return $lines[1].Trim()
}

$config = if ($env:RESU_STUDIO_CONFIG) { $env:RESU_STUDIO_CONFIG } else { Join-Path $HOME '.resu-studio' }
$cache = Join-Path $config 'python.txt'
$tried = New-Object System.Collections.Generic.List[string]

function Add-Candidate([string]$p) {
    if ($p -and -not $tried.Contains($p)) { $tried.Add($p) }
}

# 1. Chosen by the person, or found last time.
Add-Candidate $env:RESU_PYTHON
if (Test-Path -LiteralPath $cache) { Add-Candidate ((Get-Content -LiteralPath $cache -TotalCount 1).Trim()) }

# 2. An active conda environment, and conda itself.
if ($env:CONDA_PREFIX) { Add-Candidate (Join-Path $env:CONDA_PREFIX 'python.exe') }
if ($env:CONDA_EXE) { Add-Candidate (Join-Path (Split-Path (Split-Path $env:CONDA_EXE)) 'python.exe') }

# 3. The places Anaconda, Miniconda, Miniforge and Mambaforge install to.
# USERPROFILE first: it is the variable a test, or a person, can point somewhere else.
$roots = @($env:USERPROFILE, $HOME, $env:LOCALAPPDATA, $env:ProgramData, 'C:\', 'C:\tools', 'D:\')
$names = @('miniconda3', 'Miniconda3', 'anaconda3', 'Anaconda3', 'miniforge3', 'mambaforge', 'miniconda', 'anaconda')
foreach ($r in $roots) {
    if (-not $r) { continue }
    foreach ($n in $names) { Add-Candidate (Join-Path (Join-Path $r $n) 'python.exe') }
}

# 4. The Python launcher and python.org installs.
$py = Get-Command py -CommandType Application | Select-Object -First 1
if ($py) {
    $p = & $py.Source -3 -c "import sys; print(sys.executable)" 2>$null
    if ($LASTEXITCODE -eq 0 -and $p) { Add-Candidate (@($p)[0].Trim()) }
}
foreach ($base in @((Join-Path $env:LOCALAPPDATA 'Programs\Python'), $env:ProgramFiles, ${env:ProgramFiles(x86)})) {
    if ($base -and (Test-Path -LiteralPath $base)) {
        Get-ChildItem -LiteralPath $base -Directory -Filter 'Python3*' | Sort-Object Name -Descending |
            ForEach-Object { Add-Candidate (Join-Path $_.FullName 'python.exe') }
    }
}

# 5. Anything called python on the PATH, last, because the Store placeholder is usually here.
foreach ($name in @('python3', 'python')) {
    Get-Command $name -CommandType Application -All | ForEach-Object { Add-Candidate $_.Source }
}

foreach ($exe in $tried) {
    $real = Test-Python $exe
    if ($real) {
        try {
            New-Item -ItemType Directory -Force -Path $config | Out-Null
            Set-Content -LiteralPath $cache -Value $real -Encoding UTF8
        } catch { }
        Write-Output $real
        exit 0
    }
}

[Console]::Error.WriteLine("resu-studio: no Python 3.8 or newer was found. Looked in the conda folders " +
    "(miniconda3, anaconda3, miniforge3, mambaforge) under your user folder, AppData\Local, ProgramData " +
    "and C:\, the py launcher, python.org installs, and the PATH. If Python is installed somewhere " +
    "else, set RESU_PYTHON to its python.exe. Otherwise it can be installed from python.org.")
exit 1
