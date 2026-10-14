import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path


class WrapperGenerator:
    def __init__(self, project_root: str, gradle_version: str = "9.3.1"):
        self.root = Path(project_root).resolve()
        self.gradle_version = gradle_version

    def wrapper_is_complete(self) -> bool:
        required = [
            self.root / "gradlew",
            self.root / "gradlew.bat",
            self.root / "gradle" / "wrapper" / "gradle-wrapper.jar",
            self.root / "gradle" / "wrapper" / "gradle-wrapper.properties",
        ]

        return all(path.exists() for path in required)

    def find_gradle_command(self) -> str | None:
        return shutil.which("gradle")

    def make_gradlew_executable(self) -> None:
        gradlew = self.root / "gradlew"

        if gradlew.exists():
            current_mode = gradlew.stat().st_mode
            gradlew.chmod(
                current_mode
                | stat.S_IXUSR
                | stat.S_IXGRP
                | stat.S_IXOTH
            )

    def generate_wrapper(self) -> bool:
        if self.wrapper_is_complete():
            print("Gradle Wrapper already exists.")
            self.make_gradlew_executable()
            return True

        gradle_command = self.find_gradle_command()

        if not gradle_command:
            print(
                "Gradle is not installed. "
                "The GitHub workflow must install Gradle before running this script."
            )
            return False

        temporary_build_file = self.root / "build.gradle"
        created_temporary_file = False

        if not temporary_build_file.exists() and not (
            self.root / "build.gradle.kts"
        ).exists():
            temporary_build_file.write_text(
                "// Temporary file used to generate the Gradle Wrapper.\n",
                encoding="utf-8",
            )
            created_temporary_file = True

        command = [
            gradle_command,
            "wrapper",
            "--gradle-version",
            self.gradle_version,
            "--distribution-type",
            "bin",
        ]

        print(f"Generating Gradle Wrapper {self.gradle_version}...")

        try:
            subprocess.run(
                command,
                cwd=self.root,
                check=True,
                text=True,
            )
        except subprocess.CalledProcessError as error:
            print(f"Failed to generate Gradle Wrapper: {error}")
            return False
        finally:
            if created_temporary_file and temporary_build_file.exists():
                temporary_build_file.unlink()

        self.make_gradlew_executable()

        if not self.wrapper_is_complete():
            print("Gradle ran, but some wrapper files are still missing.")
            return False

        print("Gradle Wrapper created successfully.")
        return True


def main() -> int:
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."
    gradle_version = (
        sys.argv[2] if len(sys.argv) > 2 else "9.3.1"
    )

    generator = WrapperGenerator(project_root, gradle_version)

    return 0 if generator.generate_wrapper() else 1


if __name__ == "__main__":
    raise SystemExit(main())
