#!/usr/bin/env python3
"""Fingerprint an extracted source tree and choose a supported build adapter."""
from pathlib import Path
import json, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
SKIP = {".git", ".gradle", ".godot", "node_modules", "build", "dist", ".venv"}
def files():
    for p in root.rglob("*"):
        if not p.is_file() or any(part in SKIP for part in p.parts):
            continue
        yield p
all_files = list(files())
names = {p.name.lower() for p in all_files}
relpaths = {p.relative_to(root).as_posix().lower() for p in all_files}

def find(name):
    return next((p for p in all_files if p.name.lower() == name.lower()), None)

def choose():
    # Prefer native project markers over source-file guesses.
    godot = find("project.godot")
    if godot:
        return "godot", godot.parent
    pubspec = find("pubspec.yaml")
    if pubspec and any(p.name.lower() == "lib" and p.is_dir() for p in pubspec.parent.iterdir()):
        return "flutter", pubspec.parent
    package_json = find("package.json")
    if package_json and ("android" in relpaths or any(p.name.lower() == "app.json" for p in all_files)):
        # React Native Android projects have an android folder and package.json.
        if any(p.relative_to(root).parts and p.relative_to(root).parts[0].lower() == "android" for p in all_files):
            return "react-native-android", package_json.parent
    settings = next((p for p in all_files if p.name.lower() in {"settings.gradle", "settings.gradle.kts"}), None)
    if settings:
        # An exported engine project may have Gradle but should be routed by its engine marker above.
        return "android-gradle", settings.parent
    # Android projects sometimes omit settings.gradle but include an app module build file.
    app_gradle = next((p for p in all_files if p.name.lower() in {"build.gradle", "build.gradle.kts"} and p.parent.name.lower() == "app"), None)
    if app_gradle and any(p.name.lower() == "gradlew" for p in all_files):
        return "android-gradle", app_gradle.parent.parent
    # Web-only sources cannot be compiled into an APK safely without a configured wrapper.
    if find("package.json") or find("index.html"):
        return "web-or-node", root
    return "unknown", root

kind, project_dir = choose()
result = {
    "project_type": kind,
    "project_dir": str(project_dir),
    "relative_project_dir": str(project_dir.relative_to(root)) if project_dir != root else ".",
    "file_count": len(all_files),
}
print(json.dumps(result))
if kind == "unknown":
    print("ERROR: No supported project marker found (project.godot, pubspec.yaml, or Android Gradle settings).", file=sys.stderr)
    sys.exit(2)
