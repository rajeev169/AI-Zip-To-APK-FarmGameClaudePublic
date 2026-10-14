import os
import shutil

class ProjectRepairer:

    def __init__(self, root):
        self.root = root
        self.report = []

    def file_exists(self, name):
        for path, dirs, files in os.walk(self.root):
            if name in files:
                return os.path.join(path, name)
        return None

    def create_local_properties(self):
        if not self.file_exists("local.properties"):
            with open(os.path.join(self.root, "local.properties"), "w") as f:
                f.write("sdk.dir=/opt/android-sdk\n")
            self.report.append("Created local.properties")

    def check_gradle(self):
        if not self.file_exists("settings.gradle") and \
           not self.file_exists("settings.gradle.kts"):
            self.report.append("Missing settings.gradle")

        if not self.file_exists("build.gradle") and \
           not self.file_exists("build.gradle.kts"):
            self.report.append("Missing build.gradle")

    def check_manifest(self):
        if not self.file_exists("AndroidManifest.xml"):
            self.report.append("Missing AndroidManifest.xml")

    def repair(self):
        self.create_local_properties()
        self.check_gradle()
        self.check_manifest()
        return self.report


if __name__ == "__main__":
    repairer = ProjectRepairer(".")
    print(repairer.repair())
