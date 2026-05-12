import subprocess
import sys


def _run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def main() -> None:
    global_flag = "--global" in sys.argv[1:]

    scope = ["--global"] if global_flag else []

    _run(["git", "config", *scope, "diff.knxplain.textconv", "knxshow"])
    _run(["git", "config", *scope, "diff.knxplain.cachetextconv", "true"])

    if not global_flag:
        gitattributes = ".gitattributes"
        line = "*.knxproj diff=knxplain\n"
        try:
            with open(gitattributes) as f:
                if line in f.read():
                    return
        except FileNotFoundError:
            pass
        with open(gitattributes, "a") as f:
            f.write(line)
        print(f"Updated {gitattributes}")

    scope_label = "global" if global_flag else "local"
    print(f"Configured git textconv driver ({scope_label}): *.knxproj → knxshow")
