import json
import sys
from pathlib import Path


class DependencyResolver:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()
        self.report = {
            "project_root": str(self.project_root),
            "gradle_files": [],
            "repositories": [],
            "dependencies": [],
            "warnings": [],
        }

    def find_gradle_files(self) -> list[Path]:
        gradle_files = []

        for path in self.project_root.rglob("*"):
            if path.is_file() and path.name in {
                "build.gradle",
                "build.gradle.kts",
                "settings.gradle",
                "settings.gradle.kts",
            }:
                gradle_files.append(path)

        return sorted(gradle_files)

    def detect_dsl(self, path: Path) -> str:
        if path.suffix == ".kts":
            return "kotlin"

        return "groovy"

    def scan_file(self, path: Path) -> dict:
        content = path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        file_result = {
            "path": str(path),
            "dsl": self.detect_dsl(path),
            "has_google_repository": "google()" in content,
            "has_maven_central": "mavenCentral()" in content,
            "has_dependencies_block": "dependencies" in content,
            "detected_dependencies": [],
        }

        dependency_markers = [
            "implementation(",
            "api(",
            "compileOnly(",
            "runtimeOnly(",
            "testImplementation(",
            "androidTestImplementation(",
            "implementation ",
            "api ",
            "compileOnly ",
            "runtimeOnly ",
        ]

        for line in content.splitlines():
            stripped = line.strip()

            if any(
                stripped.startswith(marker)
                for marker in dependency_markers
            ):
                file_result["detected_dependencies"].append(stripped)

        return file_result

    def analyze(self) -> dict:
        gradle_files = self.find_gradle_files()

        if not gradle_files:
            self.report["warnings"].append(
                "No Gradle configuration files were found."
            )

        for path in gradle_files:
            result = self.scan_file(path)

            self.report["gradle_files"].append(result)

            if result["has_google_repository"]:
                self.report["repositories"].append(
                    {
                        "file": str(path),
                        "repository": "google",
                    }
                )

            if result["has_maven_central"]:
                self.report["repositories"].append(
                    {
                        "file": str(path),
                        "repository": "mavenCentral",
                    }
                )

            for dependency in result["detected_dependencies"]:
                self.report["dependencies"].append(
                    {
                        "file": str(path),
                        "value": dependency,
                    }
                )

        if not any(
            item["repository"] == "google"
            for item in self.report["repositories"]
        ):
            self.report["warnings"].append(
                "The google() repository was not detected."
            )

        if not any(
            item["repository"] == "mavenCentral"
            for item in self.report["repositories"]
        ):
            self.report["warnings"].append(
                "The mavenCentral() repository was not detected."
            )

        return self.report

    def dependency_exists(self, dependency_text: str) -> bool:
        for item in self.report["dependencies"]:
            if dependency_text in item["value"]:
                return True

        return False

    def save_report(self) -> Path:
        report_path = (
            self.project_root
            / "dependency-report.json"
        )

        report_path.write_text(
            json.dumps(self.report, indent=2),
            encoding="utf-8",
        )

        return report_path


def main() -> int:
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."

    resolver = DependencyResolver(project_root)
    report = resolver.analyze()
    report_path = resolver.save_report()

    print(json.dumps(report, indent=2))
    print(f"Dependency report created: {report_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
