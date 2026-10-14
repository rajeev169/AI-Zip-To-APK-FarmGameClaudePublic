import subprocess
import sys
from pathlib import Path


class BuildEngine:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()
        self.log_path = self.project_root / "gradle-build.log"

    def find_wrapper(self) -> Path | None:
        direct_wrapper = self.project_root / "gradlew"

        if direct_wrapper.exists():
            return direct_wrapper

        for wrapper in self.project_root.rglob("gradlew"):
            if wrapper.is_file():
                return wrapper

        return None

    def find_apks(self) -> list[Path]:
        return sorted(
            path
            for path in self.project_root.rglob("*.apk")
            if "build/outputs/apk" in path.as_posix()
        )

    def build(self) -> bool:
        wrapper = self.find_wrapper()

        if wrapper is None:
            print("Gradle wrapper was not found.")
            return False

        working_directory = wrapper.parent

        print(f"Using Gradle wrapper: {wrapper}")
        print(f"Working directory: {working_directory}")
        print("Running assembleDebug...")

        command = [
            "bash",
            str(wrapper),
            "assembleDebug",
            "--stacktrace",
            "--no-daemon",
        ]

        try:
            process = subprocess.run(
                command,
                cwd=working_directory,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )

            output = process.stdout or ""

            self.log_path.write_text(
                output,
                encoding="utf-8",
            )

            print(output)

            if process.returncode != 0:
                print(
                    f"Gradle build failed with exit code "
                    f"{process.returncode}."
                )
                print(f"Build log saved: {self.log_path}")
                return False

            apks = self.find_apks()

            if not apks:
                print(
                    "Gradle completed, but no APK file was found."
                )
                return False

            print("APK build completed successfully.")

            for apk in apks:
                print(f"APK found: {apk}")

            return True

        except OSError as error:
            print(f"Could not start Gradle: {error}")
            return False


def main() -> int:
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."

    success = BuildEngine(project_root).build()

    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
