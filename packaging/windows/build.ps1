$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\\..")).Path
Set-Location $RepoRoot

Write-Host "== Momentum Windows build =="

# Ensure build-time deps exist (PyInstaller + Pillow for ICO creation).
py -m pip install --upgrade pip | Out-Host
py -m pip install -r requirements.txt | Out-Host
py -m pip install pyinstaller pillow | Out-Host

# Create .ico if missing/outdated.
py .\packaging\windows\make_icon.py | Out-Host

# Build (one-folder is most reliable for Qt apps; easy to distribute as a zip).
py -m PyInstaller .\momentum.spec --clean --noconfirm | Out-Host

Write-Host ""
Write-Host "Built app is at: $RepoRoot\\dist\\Momentum\\Momentum.exe"

