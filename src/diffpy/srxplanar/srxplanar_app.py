import argparse

from diffpy.srxplanar.version import __version__  # noqa


def main():
    parser = argparse.ArgumentParser(
        prog="diffpy.srxplanar",
        description=(
            "2D diffraction image integration using non "
            "splitting pixel algorithm\n\nFor more information, visit: "
            "https://github.com/diffpy/diffpy.srxplanar/"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--version",
        action="store_true",
        help="Show the program's version number and exit",
    )

    args = parser.parse_args()

    if args.version:
        print(f"diffpy.srxplanar {__version__}")
    else:
        # Default behavior when no arguments are given
        parser.print_help()


if __name__ == "__main__":
    main()
