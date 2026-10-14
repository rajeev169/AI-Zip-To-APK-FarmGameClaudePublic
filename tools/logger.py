import os
import datetime

class BuildLogger:
    def __init__(self, log_file="build.log"):
        self.log_file = log_file

    def write(self, level, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        line = f"[{timestamp}] [{level}] {message}\n"

        print(line.strip())

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(line)

    def info(self, message):
        self.write("INFO", message)

    def warning(self, message):
        self.write("WARNING", message)

    def error(self, message):
        self.write("ERROR", message)

    def success(self, message):
        self.write("SUCCESS", message)


if __name__ == "__main__":
    logger = BuildLogger()

    logger.info("Logger started.")
    logger.success("Everything works.")
    logger.warning("This is a warning.")
    logger.error("This is an error.")
