import subprocess


def _run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def setup(global_flag: bool = False) -> None:
    scope = ["--global"] if global_flag else []

    _run(["git", "config", *scope, "diff.knxray.textconv", "knxray show"])
    _run(["git", "config", *scope, "diff.knxray.cachetextconv", "true"])

    if not global_flag:
        gitattributes = ".gitattributes"
        line = "*.knxproj diff=knxray\n"
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
    print(f"Configured git textconv driver ({scope_label}): *.knxproj → knxray show")
