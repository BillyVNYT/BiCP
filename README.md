# BiCP

BiCP is a lightweight desktop IDE designed specifically for Competitive Programming.

## Features

- C++ code editing with line numbers
- Python code editing and execution
- Run, Rebuild, and Stop controls
- Standard input panel
- Read-only output panel for stdout, stderr, compile errors, runtime errors, exit codes, and timeout messages
- Fixed local workspace managed by the app
- Save and Save As
- Find in editor
- C++ and Python language switching
- Settings window with categorized pages
- Persistent configuration
- Language preference persistence
- Editor font size and tab size configuration
- C++ compiler configuration
- Python interpreter configuration
- Editable default C++ and Python templates

## Screenshots

Screenshots will be added in a future release.

## Requirements

- Windows 10/11 x64
- Python 3.12 or newer when running from source
- PySide6 when running from source
- g++ available in PATH for compiling and running C++ programs

The packaged Windows build bundles Python and application dependencies, but C++ execution still requires a working g++ installation in PATH.

## Installation

Download the Windows release archive, extract it, and run `BiCP.exe`.

## Build From Source

```powershell
git clone https://github.com/<your-user>/BiCP.git
cd BiCP
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

To build the Windows executable:

```powershell
python -m pip install -r requirements.txt pyinstaller
python scripts/build.py
```

The build output is created under `dist/BiCP/`.

## Project Structure

- `core/` contains workspace, compiler, runner, and version logic.
- `ui/` contains PySide6 windows, menus, and editor widgets.
- `config/` contains default persistent application settings.
- `workspace/` is the local runtime workspace created and updated by the app.
- `assets/` contains application assets such as icons.
- `scripts/` contains developer automation such as the PyInstaller build script.
- `tests/` contains smoke tests for non-GUI core behavior.

## Keyboard Shortcuts

- `Ctrl+S`: Save
- `Ctrl+Shift+S`: Save As
- `Ctrl+F`: Find
- `Ctrl+,`: Settings

## Versioning

- `v1.0.0`: initial stable release
- `v1.1.0`: settings release

## License

No license has been selected yet. Add a license before distributing BiCP publicly.
