import argparse

from src.app import main as launch_app
from src.dependency_audit import print_dependency_report


def main():
    parser = argparse.ArgumentParser(prog="weather-app")
    parser.add_argument(
        "--check-deps",
        action="store_true",
        help="Print a dependency audit and exit without launching the app.",
    )
    args = parser.parse_args()

    if args.check_deps:
        raise SystemExit(print_dependency_report())

    launch_app()


if __name__ == "__main__":
    main()
