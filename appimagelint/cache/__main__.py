import argparse
import logging
import sys

from .cli import bundle_metadata


from .._logging import setup
setup(loglevel=logging.DEBUG, with_timestamps=True)

logging.getLogger("urllib3").setLevel(logging.INFO)


parser = argparse.ArgumentParser(
        prog="appimagelint",
        description="Run compatibility and other checks on AppImages automatically, "
                    "and provide human-understandable feedback"
    )

parser.add_argument("command", nargs=1, help="Command to run")

args = parser.parse_args()

available_commands = ("bundle_metadata",)

command = args.command[0]

if command == "bundle_metadata":
    bundle_metadata()

else:
    print("Unknown command", command, file=sys.stderr)
    print("Available commands:", " ".join(available_commands), file=sys.stderr)
