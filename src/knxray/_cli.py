import argparse
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(prog="knxray")
    subparsers = parser.add_subparsers(dest="command")

    show_p = subparsers.add_parser("show", help="Parse → JSON (xknxproject) to stdout")
    show_p.add_argument("file", metavar="<file.knxproj>")

    diff_p = subparsers.add_parser("diff", help="JSON diff to stdout")
    diff_p.add_argument("file1", metavar="<file1.knxproj>")
    diff_p.add_argument("file2", metavar="<file2.knxproj>")

    setup_p = subparsers.add_parser("setup", help="Configure git textconv for *.knxproj")
    setup_p.add_argument("--global", dest="global_flag", action="store_true")

    args = parser.parse_args()

    if args.command == "show":
        from knxray._show import show
        show(Path(args.file))
    elif args.command == "diff":
        from knxray._diff import diff
        diff(Path(args.file1), Path(args.file2))
    elif args.command == "setup":
        from knxray._setup import setup
        setup(args.global_flag)
    else:
        parser.print_help()
        sys.exit(1)
