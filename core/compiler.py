import shutil
from pathlib import Path


class Compiler:
    def __init__(
        self,
        compiler_name: str = "g++",
        standard: str = "c++20",
        optimization: str = "O0",
    ) -> None:
        self.compiler_name = compiler_name
        self.standard = standard
        self.optimization = optimization

    def is_available(self) -> bool:
        return shutil.which(self.compiler_name) is not None

    def compile_arguments(self, source_path: Path, executable_path: Path) -> list[str]:
        return [
            str(source_path),
            f"-std={self.standard}",
            f"-{self.optimization}",
            "-o",
            str(executable_path),
        ]

    def configure(
        self,
        compiler_name: str,
        standard: str,
        optimization: str,
    ) -> None:
        self.compiler_name = compiler_name
        self.standard = standard
        self.optimization = optimization
