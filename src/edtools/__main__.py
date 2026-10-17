"""python -m edtools <command> '<json args>'  ->  JSON on stdout.

Exit 0: {"result": ...}. Exit 2: {"error": "..."} caused by bad arguments; the caller
shows it to the model so it can correct itself. Any other exit is a bug or a crash.
"""

import json
import sys

from edtools.commands import COMMANDS, UserError


def main() -> int:
    if len(sys.argv) != 3 or sys.argv[1] not in COMMANDS:
        print(json.dumps({"error": f"usage: edtools <{'|'.join(COMMANDS)}> '<json>'"}))
        return 2
    try:
        args = json.loads(sys.argv[2])
        print(json.dumps({"result": COMMANDS[sys.argv[1]](**args)}, default=str))
        return 0
    except (UserError, TypeError, json.JSONDecodeError) as e:
        print(json.dumps({"error": str(e)}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
