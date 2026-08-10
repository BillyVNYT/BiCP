import shutil
from pathlib import Path


class Compiler:
    def __init__(self, compiler_name: str = "g++") -> None:
        self.compiler_name = compiler_name

    def is_available(self) -> bool:
        return shutil.which(self.compiler_name) is not None

    def compile_arguments(self, source_path: Path, executable_path: Path) -> list[str]:
        return [
            str(source_path),
            "-std=c++20",
            "-O0",
            "-o",
            str(executable_path),
        ]
