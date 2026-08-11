from pathlib import Path

DEFAULT_SETTINGS = {
    "theme": "dark",
    "font_size": "14",
    "tab_size": "4",
    "language": "cpp"
}

class SettingManager:
    def __init__(self, path: Path | None = None):
        self.path = (
            path
            or Path(__file__).resolve().parents[1]
            / "config"
            / "setting.txt"
        )
        self.settings = DEFAULT_SETTINGS.copy()

    def load(self):
        self.settings = DEFAULT_SETTINGS.copy()
        if not self.path.exists():
            self.save()
            return

        try:
            text = self.path.read_text(encoding="utf-8")
            for line in text.splitlines():
                line = line.strip()
                if not line:
                    continue
                if line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                if key in self.settings:
                    self.settings[key] = value

        except OSError as exc:
            print(f"Could not load settings: {exc}")

    def save(self) -> None:
        try:
            self.path.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            lines = []

            for key, value in self.settings.items():
                lines.append(
                    f"{key}={value}"
                )

            self.path.write_text(
                "\n".join(lines) + "\n",
                encoding="utf-8"
            )

        except OSError as exc:
            print(
                f"Could not save settings: {exc}"
            )

    def get(self, key: str):
        return self.settings.get(key)
    
    def set(self, key: str, value):
        if key not in self.settings:
            return
        self.settings[key] = str(value)