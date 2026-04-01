# Momentum

Offline course learning tracker (PySide6).

## Quickstart (development)

### Prereqs

- Windows 10/11
- Python 3.10+ (the `py` launcher available)

### Create venv + install

From the repo root:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -U pip
py -m pip install -r requirements.txt
```

### Run

```powershell
py main.py
```

## Data / database location

Momentum stores its local SQLite DB in your home directory:

- **Windows**: `C:\Users\<you>\.momentum\momentum.db`

The app will create the folder on first run.

## Packaging (Windows .exe)

Packaging is done with PyInstaller and embeds:

- **EXE icon**: `resources/icons/momentum.ico`
- **Windows version metadata**: `packaging/windows/version_info.txt`

### Build (one command)

From the repo root:

```powershell
.\packaging\windows\build.ps1
```

Output:

- **`dist\Momentum.exe`**

### Run the packaged app

```powershell
.\dist\Momentum.exe
```

## Build & release checklist

- **Update version**:
  - `momentum/config.py` → `Config.VERSION`
  - `packaging/windows/version_info.txt` → `FileVersion` / `ProductVersion` / `filevers` / `prodvers`
- **Clean build**:

```powershell
Remove-Item -Recurse -Force .\build,.\dist -ErrorAction SilentlyContinue
.\packaging\windows\build.ps1
```

- **Smoke test**:
  - Launch `dist\Momentum.exe`
  - Confirm app starts, DB is created/updated, and the icon/metadata look correct in Task Manager / Explorer Properties.
- **Create a release artifact**:
  - Recommended: zip the executable for sharing:

```powershell
Compress-Archive -Force .\dist\Momentum.exe .\dist\Momentum-win-x64.zip
```

- **(Optional) Sign the exe** (best UX on Windows):
  - Use your code-signing cert with `signtool.exe` (Windows SDK).

