from pathlib import Path
from PySide6.QtCore import QStandardPaths

DEFAULT_CPP = """#include <bits/stdc++.h>
using namespace std;

int main() {
    return 0;
}
"""


DEFAULT_PYTHON = """def main():
    pass


if __name__ == "__main__":
    main()
"""


DEFAULT_SETTINGS = {
    "theme": "dark",
    "font_size": "14",
    "tab_size": "4",
    "language": "cpp",
    "cpp_compiler": "g++",
    "cpp_standard": "c++20",
    "cpp_optimization": "O0",
    "run_timeout_ms": "3000",
    "python_interpreter": "",
    "default_cpp": DEFAULT_CPP,
    "default_python": DEFAULT_PYTHON,
}


MULTILINE_KEYS = {
    "default_cpp",
    "default_python",
}


class SettingManager:
    def __init__(self, path: Path | None = None):

        if path is not None:
            self.path = path

        else:
            app_data = QStandardPaths.writableLocation(
                QStandardPaths.AppLocalDataLocation
            )

            self.path = (
                Path(app_data)
                / "settings"
                / "setting.txt"
            )

        self.settings = DEFAULT_SETTINGS.copy()

    def load(self) -> None:
        self.settings = DEFAULT_SETTINGS.copy()
        if not self.path.exists():
            self.save()
            return

        try:
            lines = self.path.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            print(f"Could not load settings: {exc}")
            return

        index = 0
        while index < len(lines):
            line = lines[index].strip()
            index += 1

            if not line or line.startswith("#"):
                continue

            if line.startswith("[") and line.endswith("]") and not line.startswith("[/"):
                key = line[1:-1].strip()
                end_marker = f"[/{key}]"
                block_lines = []
                while index < len(lines) and lines[index].strip() != end_marker:
                    block_lines.append(lines[index])
                    index += 1
                if index < len(lines):
                    index += 1
                if key in MULTILINE_KEYS:
                    self.settings[key] = "\n".join(block_lines).rstrip() + "\n"
                continue

            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if key in self.settings:
                self.settings[key] = value

    def save(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            scalar_lines = []
            block_lines = []

            for key, value in self.settings.items():
                if key in MULTILINE_KEYS:
                    block_lines.extend([f"[{key}]", str(value).rstrip(), f"[/{key}]"])
                else:
                    scalar_lines.append(f"{key}={value}")

            text = "\n".join(scalar_lines + [""] + block_lines) + "\n"
            self.path.write_text(text, encoding="utf-8")
        except OSError as exc:
            print(f"Could not save settings: {exc}")

    def get(self, key: str, fallback: str = "") -> str:
        return self.settings.get(key, fallback)

    def get_int(self, key: str, fallback: int) -> int:
        try:
            return int(self.get(key))
        except (TypeError, ValueError):
            return fallback

    def set(self, key: str, value) -> None:
        if key not in self.settings:
            return
        self.settings[key] = str(value)
