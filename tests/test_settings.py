from pathlib import Path

from core.setting import SettingManager


def test_settings_persist_language(tmp_path: Path) -> None:
    settings_path = tmp_path / "setting.txt"
    settings = SettingManager(settings_path)
    settings.load()
    settings.set("language", "python")
    settings.save()

    reloaded = SettingManager(settings_path)
    reloaded.load()

    assert reloaded.get("language") == "python"


def test_settings_persist_default_templates(tmp_path: Path) -> None:
    settings_path = tmp_path / "setting.txt"
    settings = SettingManager(settings_path)
    settings.load()
    settings.set("default_cpp", "int main() { return 0; }\n")
    settings.set("default_python", "print('ok')\n")
    settings.save()

    reloaded = SettingManager(settings_path)
    reloaded.load()

    assert reloaded.get("default_cpp") == "int main() { return 0; }\n"
    assert reloaded.get("default_python") == "print('ok')\n"
