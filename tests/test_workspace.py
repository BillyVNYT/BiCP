from pathlib import Path

from core.workspace import WorkspaceManager


def test_workspace_creates_default_files(tmp_path: Path) -> None:
    workspace = WorkspaceManager(project_root=tmp_path)
    workspace.ensure()

    assert workspace.workspace_dir.exists()
    assert (workspace.workspace_dir / "main.cpp").exists()
    assert (workspace.workspace_dir / "main.py").exists()
    assert workspace.input_path.exists()
    assert workspace.output_path.exists()


def test_language_source_paths(tmp_path: Path) -> None:
    workspace = WorkspaceManager(project_root=tmp_path)
    workspace.ensure()

    workspace.set_language("cpp")
    assert workspace.get_source_path().name == "main.cpp"

    workspace.set_language("python")
    assert workspace.get_source_path().name == "main.py"
