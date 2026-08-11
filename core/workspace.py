from pathlib import Path

from core.setting import DEFAULT_CPP, DEFAULT_PYTHON

from PySide6.QtCore import QStandardPaths

class WorkspaceError(RuntimeError):
    pass


class WorkspaceManager:

    def __init__(self, project_root: Path | None = None):

        if project_root is not None:
            self.project_root = project_root

        else:
            app_data = QStandardPaths.writableLocation(
                QStandardPaths.AppLocalDataLocation
            )

            self.project_root = Path(app_data)

        self.workspace_dir = (
            self.project_root / "workspace"
        )

        self.source_path = (
            self.workspace_dir / "main.cpp"
        )

        self.executable_path = (
            self.workspace_dir / "main.exe"
        )

        self.input_path = (
            self.workspace_dir / "input.txt"
        )

        self.output_path = (
            self.workspace_dir / "output.txt"
        )

        # Ngôn ngữ mặc định
        self.current_language = "cpp"
        self.default_cpp = DEFAULT_CPP
        self.default_python = DEFAULT_PYTHON

    # =====================================================
    # LANGUAGE
    # =====================================================

    def set_language(self, language: str) -> None:

        if language not in ("cpp", "python"):
            raise WorkspaceError(
                f"Unsupported language: {language}"
            )

        self.current_language = language

    # =====================================================
    # PATH
    # =====================================================

    def get_source_path(self) -> Path:

        if self.current_language == "cpp":
            return self.workspace_dir / "main.cpp"

        if self.current_language == "python":
            return self.workspace_dir / "main.py"

        raise WorkspaceError(
            f"Unsupported language: {self.current_language}"
        )

    def get_executable_path(self) -> Path:

        if self.current_language == "cpp":
            return self.workspace_dir / "main.exe"

        # Python không cần executable
        raise WorkspaceError(
            "Python does not have an executable path"
        )

    # =====================================================
    # DEFAULT CODE
    # =====================================================

    def get_default_code(self) -> str:

        if self.current_language == "cpp":
            return self.default_cpp

        if self.current_language == "python":
            return self.default_python

        raise WorkspaceError(
            f"Unsupported language: {self.current_language}"
        )

    # =====================================================
    # ENSURE WORKSPACE
    # =====================================================

    def ensure(self) -> None:

        try:

            self.workspace_dir.mkdir(
                parents=True,
                exist_ok=True
            )

            # -----------------------------
            # C++
            # -----------------------------

            cpp_path = (
                self.workspace_dir / "main.cpp"
            )

            if not cpp_path.exists():

                cpp_path.write_text(
                    self.default_cpp,
                    encoding="utf-8"
                )

            # -----------------------------
            # Python
            # -----------------------------

            python_path = (
                self.workspace_dir / "main.py"
            )

            if not python_path.exists():

                python_path.write_text(
                    self.default_python,
                    encoding="utf-8"
                )

            # -----------------------------
            # Input
            # -----------------------------

            if not self.input_path.exists():

                self.input_path.write_text(
                    "5\n",
                    encoding="utf-8"
                )

            # -----------------------------
            # Output
            # -----------------------------

            if not self.output_path.exists():

                self.output_path.write_text(
                    "",
                    encoding="utf-8"
                )

        except OSError as exc:

            raise WorkspaceError(
                f"Could not prepare workspace: {exc}"
            ) from exc

    def set_default_code(
        self,
        language: str,
        code: str,
    ) -> None:

        if language == "cpp":
            self.default_cpp = code
            return

        if language == "python":
            self.default_python = code
            return

        raise WorkspaceError(
            f"Unsupported language: {language}"
        )

    # =====================================================
    # CODE
    # =====================================================

    def load_code(self) -> str:

        source_path = self.get_source_path()

        try:

            return source_path.read_text(
                encoding="utf-8"
            )

        except OSError as exc:

            raise WorkspaceError(
                f"Could not load {source_path.name}: {exc}"
            ) from exc

    # -----------------------------------------------------

    def save_code(self, code: str) -> None:

        source_path = self.get_source_path()

        try:

            source_path.write_text(
                code,
                encoding="utf-8"
            )

        except OSError as exc:

            raise WorkspaceError(
                f"Could not save {source_path.name}: {exc}"
            ) from exc

    # =====================================================
    # INPUT
    # =====================================================

    def load_input(self) -> str:

        try:

            return self.input_path.read_text(
                encoding="utf-8"
            )

        except OSError:

            return ""

    # -----------------------------------------------------

    def save_input(self, input_data: str) -> None:

        try:

            self.input_path.write_text(
                input_data,
                encoding="utf-8"
            )

        except OSError as exc:

            raise WorkspaceError(
                f"Could not save input.txt: {exc}"
            ) from exc

    # =====================================================
    # OUTPUT
    # =====================================================

    def save_output(self, output: str) -> None:

        try:

            self.output_path.write_text(
                output,
                encoding="utf-8"
            )

        except OSError as exc:

            raise WorkspaceError(
                f"Could not save output.txt: {exc}"
            ) from exc
