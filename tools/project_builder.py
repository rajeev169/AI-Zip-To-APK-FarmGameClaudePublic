import json
import sys
from pathlib import Path

try:
    from .auto_repair import AutoRepair
    from .build_engine import BuildEngine
    from .dependency_resolver import DependencyResolver
    from .detect_project import ProjectDetector
    from .gradle_generator import GradleGenerator
    from .manifest_generator import ManifestGenerator
    from .wrapper_generator import WrapperGenerator
except ImportError:
    from auto_repair import AutoRepair
    from build_engine import BuildEngine
    from dependency_resolver import DependencyResolver
    from detect_project import ProjectDetector
    from gradle_generator import GradleGenerator
    from manifest_generator import ManifestGenerator
    from wrapper_generator import WrapperGenerator


class ProjectBuilder:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()

        self.result = {
            "project_root": str(self.project_root),
            "detected": {},
            "repair": {},
            "dependencies": {},
            "wrapper_created": False,
            "build_success": False,
        }

    def detect_project(self) -> None:
        print("\n[1/6] Detecting project...")

        detector = ProjectDetector(str(self.project_root))
        self.result["detected"] = detector.detect()

        print(json.dumps(self.result["detected"], indent=2))

    def inspect_and_repair(self) -> None:
        print("\n[2/6] Inspecting missing files...")

        repairer = AutoRepair(str(self.project_root))
        self.result["repair"] = repairer.repair()

    def generate_safe_files(self) -> None:
        print("\n[3/6] Generating safe configuration files...")

        # These generators only create files when missing.
        GradleGenerator(str(self.project_root)).generate()
        ManifestGenerator(str(self.project_root)).generate()

    def analyze_dependencies(self) -> None:
        print("\n[4/6] Analyzing dependencies...")

        resolver = DependencyResolver(str(self.project_root))
        self.result["dependencies"] = resolver.analyze()
        resolver.save_report()

    def prepare_wrapper(self) -> None:
        print("\n[5/6] Preparing Gradle Wrapper...")

        wrapper = WrapperGenerator(str(self.project_root))
        self.result["wrapper_created"] = wrapper.generate_wrapper()

        if not self.result["wrapper_created"]:
            raise RuntimeError(
                "Gradle Wrapper could not be prepared."
            )

    def build_apk(self) -> None:
        print("\n[6/6] Building debug APK...")

        engine = BuildEngine(str(self.project_root))
        self.result["build_success"] = engine.build()

        if not self.result["build_success"]:
            raise RuntimeError("APK build failed.")

    def save_result(self) -> Path:
        result_path = self.project_root / "builder-result.json"

        result_path.write_text(
            json.dumps(self.result, indent=2),
            encoding="utf-8",
        )

        print(f"\nBuilder result saved: {result_path}")
        return result_path

    def run(self) -> bool:
        print("=" * 50)
        print("AI ZIP TO APK BUILDER")
        print("=" * 50)
        print(f"Project root: {self.project_root}")

        try:
            self.detect_project()
            self.inspect_and_repair()
            self.generate_safe_files()
            self.analyze_dependencies()
            self.prepare_wrapper()
            self.build_apk()

            print("\nAPK build completed successfully.")
            return True

        except Exception as error:
            self.result["error"] = str(error)
            print(f"\nBuilder failed: {error}")
            return False

        finally:
            self.save_result()


def main() -> int:
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."

    success = ProjectBuilder(project_root).run()

    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
