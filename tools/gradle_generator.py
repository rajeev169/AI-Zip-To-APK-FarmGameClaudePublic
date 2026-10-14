import os
import sys
from pathlib import Path


class GradleGenerator:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()
        self.created_files: list[str] = []
        self.existing_files: list[str] = []

    def create_if_missing(self, relative_path: str, content: str) -> bool:
        path = self.project_root / relative_path

        if path.exists():
            print(f"Exists: {relative_path}")
            self.existing_files.append(relative_path)
            return False

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content.strip() + "\n", encoding="utf-8")

        print(f"Created: {relative_path}")
        self.created_files.append(relative_path)
        return True

    def has_settings_file(self) -> bool:
        return any(
            (self.project_root / name).exists()
            for name in (
                "settings.gradle",
                "settings.gradle.kts",
            )
        )

    def has_root_build_file(self) -> bool:
        return any(
            (self.project_root / name).exists()
            for name in (
                "build.gradle",
                "build.gradle.kts",
            )
        )

    def has_app_build_file(self) -> bool:
        return any(
            (self.project_root / name).exists()
            for name in (
                "app/build.gradle",
                "app/build.gradle.kts",
            )
        )

    def generate_gradle_properties(self) -> None:
        self.create_if_missing(
            "gradle.properties",
            """
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
android.nonTransitiveRClass=true
kotlin.code.style=official
""",
        )

    def generate_local_properties(self) -> None:
        android_sdk = os.environ.get("ANDROID_HOME")

        if not android_sdk:
            android_sdk = os.environ.get(
                "ANDROID_SDK_ROOT",
                "/usr/local/lib/android/sdk",
            )

        escaped_sdk = android_sdk.replace("\\", "\\\\")

        self.create_if_missing(
            "local.properties",
            f"sdk.dir={escaped_sdk}",
        )

    def inspect_build_files(self) -> None:
        if not self.has_settings_file():
            print(
                "Warning: settings.gradle or settings.gradle.kts "
                "is missing."
            )

        if not self.has_root_build_file():
            print(
                "Warning: root build.gradle or build.gradle.kts "
                "is missing."
            )

        if not self.has_app_build_file():
            print(
                "Warning: app/build.gradle or app/build.gradle.kts "
                "is missing."
            )

    def generate(self) -> dict:
        print(f"Preparing Gradle configuration in: {self.project_root}")

        self.inspect_build_files()
        self.generate_gradle_properties()
        self.generate_local_properties()

        result = {
            "project_root": str(self.project_root),
            "created_files": self.created_files,
            "existing_files": self.existing_files,
            "settings_found": self.has_settings_file(),
            "root_build_found": self.has_root_build_file(),
            "app_build_found": self.has_app_build_file(),
        }

        print("Gradle configuration preparation completed.")
        return result


def main() -> int:
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."

    GradleGenerator(project_root).generate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
