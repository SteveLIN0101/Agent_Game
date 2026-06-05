"""Time budget enforcement and shell command validation."""

import re
from .config import (
    HIDDEN_EVAL_PATHS,
    SHELL_FORBIDDEN,
    SHELL_WHITELIST,
    READONLY_PATHS,
)


class BudgetExceededError(Exception):
    """Raised when time budget is exhausted."""
    pass


class ForbiddenCommandError(Exception):
    """Raised when a shell command is not allowed."""
    pass


class ForbiddenPathError(Exception):
    """Raised when writing to a readonly path."""
    pass


def validate_shell_command(command: str) -> bool:
    """Check whether a shell command is in the whitelist and not forbidden.

    Supports compound commands with && and ; separators.
    Returns True if allowed, raises ForbiddenCommandError otherwise.
    """
    cmd_stripped = command.strip()

    # Split on && or ; for compound commands like "cd /x && pytest tests/"
    sub_commands = _split_compound(cmd_stripped)

    for sub_cmd in sub_commands:
        _validate_single_command(sub_cmd.strip())

    return True


def _split_compound(command: str) -> list[str]:
    """Split a compound command on && and ; separators."""
    parts = []
    current = []
    in_quote = False
    quote_char = None
    i = 0
    while i < len(command):
        ch = command[i]
        if in_quote:
            current.append(ch)
            if ch == quote_char:
                in_quote = False
        elif ch in ('"', "'"):
            in_quote = True
            quote_char = ch
            current.append(ch)
        elif command[i:i+2] == "&&":
            parts.append("".join(current).strip())
            current = []
            i += 2
            continue
        elif ch == ";":
            parts.append("".join(current).strip())
            current = []
            i += 1
            continue
        else:
            current.append(ch)
        i += 1

    if current:
        parts.append("".join(current).strip())

    return [p for p in parts if p]


def _validate_single_command(cmd: str) -> None:
    """Validate a single command against whitelist and forbidden patterns."""
    # Check forbidden patterns first
    for forbidden in SHELL_FORBIDDEN:
        if forbidden in cmd:
            raise ForbiddenCommandError(
                f"Command contains forbidden pattern: '{forbidden}'"
            )

    for hidden in HIDDEN_EVAL_PATHS:
        if _path_pattern_in_command(cmd, hidden):
            raise ForbiddenCommandError(
                f"Command references hidden evaluator path: '{hidden}'"
            )

    # Check whitelist: command must start with an allowed program
    first_word = cmd.split()[0] if cmd.split() else ""
    if not first_word:
        return

    for allowed in SHELL_WHITELIST:
        if first_word == allowed:
            return
        # Handle commands with path prefix like ./script.sh
        if first_word.startswith("./") and len(first_word) > 2:
            return  # allow relative script execution
        if cmd.startswith(allowed + " ") or cmd == allowed:
            return
    else:
        raise ForbiddenCommandError(
            f"Command '{first_word}' is not in the whitelist. "
            f"Allowed: {', '.join(SHELL_WHITELIST)}"
        )


def _path_pattern_in_command(command: str, path: str) -> bool:
    """Return True if a shell command appears to reference a hidden path."""
    normalized = command.replace("\\", "/")
    candidates = {path, path.rstrip("/")}
    if path.startswith("/"):
        candidates.add(path.rstrip("/"))
    else:
        candidates.add("./" + path.rstrip("/"))
        candidates.add("/workspace/" + path.rstrip("/"))
    return any(candidate and candidate in normalized for candidate in candidates)


def validate_read_path(path: str) -> bool:
    """Check if a file path can be read by the agent."""
    normalized = path.strip().replace("\\", "/")
    relative = normalized.lstrip("./")
    for hidden in HIDDEN_EVAL_PATHS:
        hidden_rel = hidden.lstrip("/")
        if normalized.startswith(hidden):
            raise ForbiddenPathError(
                f"Cannot read '{path}': path under '{hidden}' is hidden"
            )
        if relative.startswith(hidden_rel):
            raise ForbiddenPathError(
                f"Cannot read '{path}': path under '{hidden}' is hidden"
            )
    return True


def validate_write_path(path: str) -> bool:
    """Check if a file path can be written to by the agent.

    Returns True if allowed, raises ForbiddenPathError otherwise.
    """
    normalized = path.strip()

    for readonly in READONLY_PATHS:
        # Handle absolute paths (e.g. /opt/verifier/)
        if normalized.startswith(readonly):
            raise ForbiddenPathError(
                f"Cannot write to '{path}': path under '{readonly}' is read-only"
            )
        # Handle relative paths (e.g. tests/, ./tests/)
        relative = normalized.lstrip("./")
        if relative.startswith(readonly.lstrip("/")):
            raise ForbiddenPathError(
                f"Cannot write to '{path}': path under '{readonly}' is read-only"
            )

    return True


def check_budget(elapsed_seconds: int, budget_seconds: int) -> bool:
    """Check if time budget remains. Raises BudgetExceededError if exceeded."""
    if elapsed_seconds > budget_seconds:
        raise BudgetExceededError(
            f"Time budget of {budget_seconds}s exceeded "
            f"(elapsed: {elapsed_seconds}s). Please call submit()."
        )
    return True
