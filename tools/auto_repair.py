import json
import re
import sys
from pathlib import Path


class AutoRepair:
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir).resolve()
        self.report = {
            "project_dir": str(self.project_dir),
            "missing_files": [],
            "detected_files": [],
            "repairs": [],
        }

    def find_first(self, relative_paths: list[str]) -> Path | None:
        for relative_path in relative_paths:
            path = self.project_dir / relative_path

            if path.exists():
                return path

        return None

    def inspect(self) -> dict:
        required_groups = {
            "settings": [
                "settings.gradle",
                "settings.gradle.kts",
            ],
            "root_build": [
                "build.gradle",
                "build.gradle.kts",
            ],
            "app_build": [
                "app/build.gradle",
                "app/build.gradle.kts",
            ],
            "manifest": [
                "app/src/main/AndroidManifest.xml",
            ],
            "gradle_wrapper": [
                "gradlew",
            ],
        }

        for name, candidates in required_groups.items():
            found = self.find_first(candidates)

            if found:
                self.report["detected_files"].append(str(found))
            else:
                self.report["missing_files"].append(
                    {
                        "name": name,
                        "expected_paths": candidates,
                    }
                )

        return self.report

    def save_report(self) -> Path:
        report_path = self.project_dir / "repair-report.json"

        report_path.write_text(
            json.dumps(self.report, indent=2),
            encoding="utf-8",
        )

        return report_path

    def repair(self) -> dict:
        print(f"Inspecting project: {self.project_dir}")

        self.inspect()
        build_file = self.find_first(
            ["app/build.gradle.kts", "app/build.gradle"]
        )

        if build_file:
            print(f"Checking build file: {build_file}")

            content = build_file.read_text(
                encoding="utf-8",
                errors="ignore",
            )
            original_content = content

            if build_file.name.endswith(".kts"):
                # Remove the custom Kotlin DSL debug signing configuration.
                content = re.sub(
                    r'\n?\s*create\("debugConfig"\)\s*\{.*?\n\s*\}',
                    "",
                    content,
                    flags=re.DOTALL,
                )
                content = re.sub(
                    r'debug\s*\{\s*signingConfig\s*=\s*'
                    r'signingConfigs\.getByName\("debugConfig"\)\s*\}',
                    "debug {\n    }",
                    content,
                    flags=re.DOTALL,
                )
            else:
                # Remove the equivalent Groovy DSL configuration when present.
                content = re.sub(
                    r'\n?\s*debugConfig\s*\{.*?\n\s*\}',
                    "",
                    content,
                    flags=re.DOTALL,
                )
                content = re.sub(
                    r'debug\s*\{\s*signingConfig\s+'
                    r'signingConfigs\.debugConfig\s*\}',
                    "debug {\n    }",
                    content,
                    flags=re.DOTALL,
                )

            if content != original_content:
                build_file.write_text(
                    content,
                    encoding="utf-8",
                )
                print("Auto-repaired build.gradle file.")
                self.report["repairs"].append(
                    "Removed missing custom debug signing configuration"
                )
            else:
                print("No missing custom debug signing configuration found.")

        # Gradle Wrapper repair is handled by wrapper_generator.py.
        # Build files are never replaced with empty placeholders.
        report_path = self.save_report()

        print(f"Repair report created: {report_path}")
        print(json.dumps(self.report, indent=2))

        return self.report


def main() -> int:
    project_dir = sys.argv[1] if len(sys.argv) > 1 else "."

    AutoRepair(project_dir).repair()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
