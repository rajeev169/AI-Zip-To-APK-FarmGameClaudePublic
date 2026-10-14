import sys

try:
    from tools.project_builder import ProjectBuilder
except ImportError:
    from project_builder import ProjectBuilder


def main():
    project_dir = sys.argv[1] if len(sys.argv) > 1 else "."

    print("=" * 60)
    print("AI ZIP TO APK BUILDER")
    print("=" * 60)

    builder = ProjectBuilder(project_dir)
    result = builder.run()

    if result:
        print("\nBuild finished successfully.")
        return 0

    print("\nBuild failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
