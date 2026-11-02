"""Turn proposed edits into a human-readable patch, on the host, without changing anything."""

import difflib
import re
from collections import defaultdict
from pathlib import Path

from etl_doctor.graph.state import FileEdit


def _cosmetic(text: str) -> str:
    """Text with quote style and whitespace normalised: equal means no real change."""
    return re.sub(r"\s+", " ", text.replace("'", '"')).strip()


def _loose_pattern(text: str) -> re.Pattern:
    """old_text as a regex that ignores quote style and the width of spaces WITHIN a line.

    Line breaks must match exactly: a model that flattened a multi-line block onto one line
    must not be allowed to snap onto (and then replace) several lines it never reproduced.
    """
    out = []
    for token in re.split(r"(\n|[ \t]+)", text.strip("\n")):
        if not token:
            continue
        if token == "\n":
            out.append(r"[ \t]*\n[ \t]*")
        elif token.isspace():
            out.append(r"[ \t]+")
        else:
            out.append("".join("[\"']" if c in "\"'" else re.escape(c) for c in token))
    return re.compile("".join(out))


def repair_edits(bundle: Path, edits: list[FileEdit]) -> list[FileEdit]:
    """Snap each old_text to the file's real text when it matches exactly one place loosely.

    Models often re-quote code ('x' for "x") or reflow whitespace when copying it. If the
    loose match is unique, use the file's own text: the human reviews, and the sandbox
    validates, the diff computed from the real file, so nothing is applied blind.
    """
    fixed = []
    for e in edits:
        f = bundle / e.path
        if f.is_file():
            text = f.read_text()
            if text.count(e.old_text) != 1:
                matches = list(_loose_pattern(e.old_text).finditer(text))
                if len(matches) == 1:
                    e = e.model_copy(update={"old_text": matches[0].group(0)})
        fixed.append(e)
    return fixed


def edit_problems(bundle: Path, edits: list[FileEdit]) -> list[str]:
    from edtools.commands import UserError
    from edtools.validate import check_edit_policy

    problems = []
    try:
        check_edit_policy([e.model_dump() for e in edits])
    except UserError as e:
        problems.append(str(e))
    for e in edits:
        f = bundle / e.path
        if not f.is_file():
            problems.append(f"{e.path} does not exist")
            continue
        text = f.read_text()
        n = text.count(e.old_text)
        if n == 1:
            # Whole lines only: a fragment cut short (e.g. at a quote) can still be unique, and
            # replacing it leaves the rest of the line dangling.
            i = text.index(e.old_text)
            j = i + len(e.old_text)
            if not (i == 0 or text[i - 1] == "\n") or not (j == len(text) or text[j] == "\n" or e.old_text.endswith("\n")):
                problems.append(f"old_text in {e.path} must be complete lines; it starts or ends mid-line: {e.old_text!r}")
        if n != 1:
            problems.append(f"old_text occurs {n} times in {e.path} (must be exactly once); copy it exactly from the "
                            "file text you were given, keeping its line breaks, with enough context to be unique")
        if _cosmetic(e.old_text) == _cosmetic(e.new_text):
            problems.append(f"edit to {e.path} changes nothing but quotes or whitespace; propose a real change")
    return problems


def syntax_problems(bundle: Path, edits: list[FileEdit]) -> list[str]:
    """Does each edited file still parse? Free to check, and catches broken patches early."""
    import yaml

    problems = []
    for path, after in patched_files(bundle, edits).items():
        try:
            if path.endswith(".py"):
                compile(after, path, "exec")
            elif path.endswith((".yaml", ".yml")):
                yaml.safe_load(after)
        except (SyntaxError, yaml.YAMLError) as e:
            problems.append(f"after your edits, {path} no longer parses: {type(e).__name__}: {str(e)[:200]}")
    return problems


def patched_files(bundle: Path, edits: list[FileEdit]) -> dict[str, str]:
    by_file: dict[str, list[FileEdit]] = defaultdict(list)
    for e in edits:
        by_file[e.path].append(e)
    out = {}
    for path, file_edits in by_file.items():
        after = (bundle / path).read_text()
        for e in file_edits:
            after = after.replace(e.old_text, e.new_text, 1)
        out[path] = after
    return out


def render_patch(bundle: Path, edits: list[FileEdit]) -> str:
    out = []
    for path, after in patched_files(bundle, edits).items():
        before = (bundle / path).read_text()
        out += difflib.unified_diff(before.splitlines(keepends=True), after.splitlines(keepends=True),
                                    fromfile=f"a/{path}", tofile=f"b/{path}")
    return "".join(out)
