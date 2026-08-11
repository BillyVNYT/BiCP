from __future__ import annotations

import subprocess
import sys
from os import pathsep
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_NAME = "BiCP"
ICON_PATH = PROJECT_ROOT / "assets" / "icons" / "bicp.ico"


def main() -> int:
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--name",
        APP_NAME,
        "--windowed",
    ]

    if ICON_PATH.exists():
        command.extend(["--icon", str(ICON_PATH)])

    config_dir = PROJECT_ROOT / "config"
    if config_dir.exists():
        command.extend(["--add-data", f"{config_dir}{pathsep}config"])

    command.append(str(PROJECT_ROOT / "main.py"))
    return subprocess.call(command, cwd=PROJECT_ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
