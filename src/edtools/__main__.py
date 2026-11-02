"""python -m edtools <command> '<json args>'  ->  JSON on stdout.

Exit 0: {"result": ...}. Exit 2: {"error": "..."} caused by bad arguments; the caller
shows it to the model so it can correct itself. Any other exit is a bug or a crash.
"""

import inspect
import json
import sys

from edtools.commands import COMMANDS, UserError
from edtools.validate import HARNESS_COMMANDS

ALL = {**COMMANDS, **HARNESS_COMMANDS}


def main() -> int:
    if len(sys.argv) != 3 or sys.argv[1] not in ALL:
        print(json.dumps({"error": f"usage: edtools <{'|'.join(ALL)}> '<json>'"}))
        return 2
    try:
        args = json.loads(sys.argv[2])
        fn = ALL[sys.argv[1]]
        inspect.signature(fn).bind(**args)  # wrong/missing argument names: the caller's mistake
    except (TypeError, json.JSONDecodeError) as e:
        print(json.dumps({"error": f"bad arguments: {e}"}))
        return 2
    try:
        print(json.dumps({"result": fn(**args)}, default=str))
        return 0
    except UserError as e:
        print(json.dumps({"error": str(e)}))
        return 2
    # Anything else (a TypeError inside a command included) is our bug: crash loudly.


if __name__ == "__main__":
    sys.exit(main())
