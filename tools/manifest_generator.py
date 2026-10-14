import re
import sys
from pathlib import Path
from xml.etree import ElementTree


class ManifestGenerator:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()
        self.manifest_path = (
            self.project_root
            / "app"
            / "src"
            / "main"
            / "AndroidManifest.xml"
        )

    def find_existing_manifest(self) -> Path | None:
        if self.manifest_path.exists():
            return self.manifest_path

        for path in self.project_root.rglob("AndroidManifest.xml"):
            if path.is_file():
                return path

        return None

    def validate_manifest(self, path: Path) -> bool:
        try:
            ElementTree.parse(path)
            print(f"Valid manifest found: {path}")
            return True
        except ElementTree.ParseError as error:
            print(f"Invalid AndroidManifest.xml: {error}")
            return False
        except OSError as error:
            print(f"Could not read AndroidManifest.xml: {error}")
            return False

    def find_main_activity(self) -> tuple[str, Path] | None:
        candidates = []

        for extension in ("*.kt", "*.java"):
            for path in self.project_root.rglob(extension):
                if any(
                    ignored in path.parts
                    for ignored in ("build", ".gradle", ".git")
                ):
                    continue

                try:
                    content = path.read_text(
                        encoding="utf-8",
                        errors="ignore",
                    )
                except OSError:
                    continue

                if not re.search(
                    r"\bclass\s+MainActivity\b",
                    content,
                ):
                    continue

                package_match = re.search(
                    r"^\s*package\s+([A-Za-z_][\w.]*)",
                    content,
                    re.MULTILINE,
                )

                if package_match:
                    full_name = (
                        f"{package_match.group(1)}.MainActivity"
                    )
                    candidates.append((full_name, path))

        if not candidates:
            return None

        candidates.sort(key=lambda item: len(item[1].parts))
        return candidates[0]

    def create_manifest(
        self,
        activity_name: str,
    ) -> Path:
        self.manifest_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        content = f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <application
        android:allowBackup="true"
        android:label="Generated App"
        android:supportsRtl="true">

        <activity
            android:name="{activity_name}"
            android:exported="true">

            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>

        </activity>

    </application>

</manifest>
"""

        self.manifest_path.write_text(
            content,
            encoding="utf-8",
        )

        print(f"Created manifest: {self.manifest_path}")
        print(f"Launcher activity: {activity_name}")

        return self.manifest_path

    def generate(self) -> bool:
        existing = self.find_existing_manifest()

        if existing:
            return self.validate_manifest(existing)

        activity = self.find_main_activity()

        if activity is None:
            print(
                "AndroidManifest.xml is missing, but no "
                "MainActivity class could be detected."
            )
            print(
                "Manifest was not generated because inventing an "
                "activity name could create an invalid project."
            )
            return False

        activity_name, source_path = activity

        print(f"MainActivity detected: {source_path}")
        created = self.create_manifest(activity_name)

        return self.validate_manifest(created)


def main() -> int:
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."

    success = ManifestGenerator(project_root).generate()

    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
