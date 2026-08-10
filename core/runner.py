from __future__ import annotations

import sys
import time
from enum import Enum, auto

from PySide6.QtCore import QObject, QProcess, QTimer, Signal

from core.compiler import Compiler
from core.workspace import WorkspaceError, WorkspaceManager


class RunnerState(Enum):
    IDLE = auto()
    COMPILING = auto()
    RUNNING = auto()


class ProgramRunner(QObject):

    output_changed = Signal(str)
    busy_changed = Signal(bool)
    finished = Signal()

    def __init__(
        self,
        workspace: WorkspaceManager,
        compiler: Compiler,
        timeout_ms: int = 3000,
    ) -> None:

        super().__init__()

        self.workspace = workspace
        self.compiler = compiler
        self.timeout_ms = timeout_ms

        # Lưu code đã compile riêng cho từng ngôn ngữ
        self.last_compiled_code: dict[str, str | None] = {
            "cpp": None,
            "python": None,
        }

        self.process: QProcess | None = None

        self.state = RunnerState.IDLE

        self.pending_code = ""
        self.pending_input = ""

        self.compile_started_at = 0.0
        self.run_started_at = 0.0

        self.compile_log = ""

        self.timeout_timer = QTimer(self)
        self.timeout_timer.setSingleShot(True)
        self.timeout_timer.timeout.connect(
            self._handle_timeout
        )

    def is_busy(self) -> bool:
        return self.state is not RunnerState.IDLE

    # =====================================================
    # RUN
    # =====================================================

    def run(
        self,
        code: str,
        input_data: str,
        force_rebuild: bool = False,
    ) -> None:

        if self.state is not RunnerState.IDLE:

            self.output_changed.emit(
                "A process is already running. "
                "Stop it first."
            )

            return

        self.pending_code = code
        self.pending_input = input_data

        language = self.workspace.current_language

        # -----------------------------------------------
        # Save input
        # -----------------------------------------------

        try:

            self.workspace.save_input(
                input_data
            )

        except WorkspaceError as exc:

            self._finish_with_text(
                f"Workspace error\n\n{exc}"
            )

            return

        # -----------------------------------------------
        # Python
        # -----------------------------------------------

        if language == "python":

            self._run_python()

            return

        # -----------------------------------------------
        # C++
        # -----------------------------------------------

        if language == "cpp":

            last_code = self.last_compiled_code["cpp"]

            executable_missing = not (
                self.workspace.get_executable_path().exists()
            )

            needs_compile = (
                force_rebuild
                or code != last_code
                or executable_missing
            )

            if needs_compile:

                self._compile_cpp()

            else:

                self._run_cpp()

            return

        self._finish_with_text(
            f"Unsupported language: {language}"
        )

    # =====================================================
    # STOP
    # =====================================================

    def stop(self) -> None:

        if (
            self.process is None
            or self.state is RunnerState.IDLE
        ):
            return

        self.timeout_timer.stop()

        self.process.kill()

        self.process.waitForFinished(1000)

        self._finish_with_text(
            "Process terminated by user."
        )

    # =====================================================
    # C++ COMPILE
    # =====================================================

    def _compile_cpp(self) -> None:

        if not self.compiler.is_available():

            self._finish_with_text(
                "g++ not found\n\n"
                "Install MinGW/GCC and make sure "
                "g++ is available in PATH."
            )

            return

        try:

            self.workspace.set_language("cpp")

            self.workspace.save_code(
                self.pending_code
            )

        except WorkspaceError as exc:

            self._finish_with_text(
                f"Workspace error\n\n{exc}"
            )

            return

        self.compile_log = "Compiling...\n"

        self.output_changed.emit(
            self.compile_log
        )

        self.state = RunnerState.COMPILING

        self.busy_changed.emit(True)

        self.compile_started_at = (
            time.perf_counter()
        )

        self.process = self._create_process()

        self.process.setProgram(
            self.compiler.compiler_name
        )

        self.process.setArguments(
            self.compiler.compile_arguments(
                self.workspace.get_source_path(),
                self.workspace.get_executable_path(),
            )
        )

        self.process.start()

    # =====================================================
    # C++ RUN
    # =====================================================

    def _run_cpp(self) -> None:

        executable = (
            self.workspace.get_executable_path()
        )

        if not executable.exists():

            self._finish_with_text(
                "Executable not found.\n"
                "Rebuild the program first."
            )

            return

        self._start_program(
            str(executable),
            "C++"
        )

    # =====================================================
    # PYTHON RUN
    # =====================================================

    def _run_python(self) -> None:

        try:

            self.workspace.set_language(
                "python"
            )

            self.workspace.save_code(
                self.pending_code
            )

        except WorkspaceError as exc:

            self._finish_with_text(
                f"Workspace error\n\n{exc}"
            )

            return

        python_file = (
            self.workspace.get_source_path()
        )

        self._start_program(
            sys.executable,
            "Python",
            [str(python_file)]
        )

    # =====================================================
    # START PROGRAM
    # =====================================================

    def _start_program(
        self,
        program: str,
        language: str,
        arguments: list[str] | None = None,
    ) -> None:

        self.state = RunnerState.RUNNING

        self.busy_changed.emit(True)

        self.run_started_at = (
            time.perf_counter()
        )

        if self.compile_log:

            self.output_changed.emit(
                f"{self.compile_log}\n"
                f"Running {language}...\n"
            )

        else:

            self.output_changed.emit(
                f"Running {language}...\n"
            )

        self.process = self._create_process()

        self.process.setProgram(program)

        if arguments:
            self.process.setArguments(arguments)

        self.process.started.connect(
            self._write_program_input
        )

        self.timeout_timer.start(
            self.timeout_ms
        )

        self.process.start()

    # =====================================================
    # CREATE PROCESS
    # =====================================================

    def _create_process(self) -> QProcess:

        process = QProcess(self)

        process.setWorkingDirectory(
            str(self.workspace.workspace_dir)
        )

        process.setProcessChannelMode(
            QProcess.SeparateChannels
        )

        process.finished.connect(
            self._handle_finished
        )

        process.errorOccurred.connect(
            self._handle_process_error
        )

        return process

    # =====================================================
    # WRITE INPUT
    # =====================================================

    def _write_program_input(self) -> None:

        if self.process is None:
            return

        if self.pending_input:

            self.process.write(
                self.pending_input.encode("utf-8")
            )

        self.process.closeWriteChannel()

    # =====================================================
    # FINISHED
    # =====================================================

    def _handle_finished(
        self,
        exit_code: int,
        _exit_status: QProcess.ExitStatus,
    ) -> None:

        if self.process is None:
            return

        stdout = bytes(
            self.process.readAllStandardOutput()
        ).decode(
            "utf-8",
            errors="replace"
        )

        stderr = bytes(
            self.process.readAllStandardError()
        ).decode(
            "utf-8",
            errors="replace"
        )

        if self.state is RunnerState.COMPILING:

            self._handle_compile_finished(
                exit_code,
                stderr
            )

        elif self.state is RunnerState.RUNNING:

            self._handle_run_finished(
                exit_code,
                stdout,
                stderr
            )

    # =====================================================
    # COMPILE FINISHED
    # =====================================================

    def _handle_compile_finished(
        self,
        exit_code: int,
        stderr: str,
    ) -> None:

        compile_ms = (
            time.perf_counter()
            - self.compile_started_at
        ) * 1000

        if exit_code != 0:

            text = (
                "COMPILATION ERROR\n\n"
            )

            text += (
                stderr
                or f"g++ exited with code "
                   f"{exit_code}."
            )

            self._finish_with_text(
                text
            )

            return

        self.last_compiled_code["cpp"] = (
            self.pending_code
        )

        self.compile_log = (
            f"Compiled in {compile_ms:.0f} ms"
        )

        self.process = None

        self.state = RunnerState.IDLE

        # Chạy executable
        self._run_cpp()

    # =====================================================
    # PROGRAM FINISHED
    # =====================================================

    def _handle_run_finished(
        self,
        exit_code: int,
        stdout: str,
        stderr: str,
    ) -> None:

        self.timeout_timer.stop()

        run_ms = (
            time.perf_counter()
            - self.run_started_at
        ) * 1000

        text = ""

        if stdout:

            text += stdout

        if stderr:

            text += (
                "\n\nSTDERR\n"
                if text
                else "STDERR\n"
            )

            text += stderr

        if exit_code == 0:

            text += (
                f"\n\nFinished in "
                f"{run_ms:.0f} ms"
            )

        else:

            text += (
                f"\n\nRuntime Error\n"
                f"Exit code: {exit_code}\n"
                f"Finished in {run_ms:.0f} ms"
            )

        self._finish_with_text(
            text
        )

    # =====================================================
    # TIMEOUT
    # =====================================================

    def _handle_timeout(self) -> None:

        if (
            self.process is not None
            and self.state is RunnerState.RUNNING
        ):

            self.process.kill()

            self.process.waitForFinished(
                1000
            )

            self._finish_with_text(
                "Time Limit Exceeded\n\n"
                f"Program exceeded "
                f"{self.timeout_ms // 1000} seconds."
            )

    # =====================================================
    # PROCESS ERROR
    # =====================================================

    def _handle_process_error(
        self,
        error: QProcess.ProcessError,
    ) -> None:

        if error != QProcess.FailedToStart:
            return

        if self.state is RunnerState.COMPILING:

            self._finish_with_text(
                "g++ not found\n\n"
                "Install MinGW/GCC and make sure "
                "g++ is available in PATH."
            )

        elif self.state is RunnerState.RUNNING:

            self._finish_with_text(
                "Program failed to start."
            )

    # =====================================================
    # FINISH
    # =====================================================

    def _finish_with_text(
        self,
        text: str,
    ) -> None:

        self.timeout_timer.stop()

        self.state = RunnerState.IDLE

        self.process = None

        try:

            self.workspace.save_output(
                text
            )

        except WorkspaceError:

            pass

        self.output_changed.emit(
            text
        )

        self.busy_changed.emit(
            False
        )

        self.finished.emit()