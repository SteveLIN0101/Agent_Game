"""Tool call tracing for process scoring."""

from .models import ToolCall


class TraceCollector:
    """Collects and analyzes tool call logs for process scoring."""

    def __init__(self):
        self.calls: list[ToolCall] = []

    def record(self, tool_name: str, arguments: dict, success: bool = True,
               error: str | None = None, duration_ms: float = 0.0) -> ToolCall:
        import time
        call = ToolCall(
            tool_name=tool_name,
            arguments=arguments,
            timestamp=time.time(),
            success=success,
            error=error,
            duration_ms=duration_ms,
        )
        self.calls.append(call)
        return call

    def count(self) -> int:
        return len(self.calls)

    def tool_names_used(self) -> set[str]:
        return {c.tool_name for c in self.calls if c.success}

    def files_read(self) -> set[str]:
        """Extract file paths from read_file calls."""
        files = set()
        for c in self.calls:
            if c.tool_name == "openclaw__read_file" and c.success:
                path = c.arguments.get("path", "")
                if path:
                    files.add(path)
        return files

    def files_written(self) -> set[str]:
        """Extract file paths from write_file calls."""
        files = set()
        for c in self.calls:
            if c.tool_name == "openclaw__write_file" and c.success:
                path = c.arguments.get("path", "")
                if path:
                    files.add(path)
        return files

    def commands_run(self) -> list[str]:
        """Extract commands from run_shell calls."""
        cmds = []
        for c in self.calls:
            if c.tool_name == "openclaw__run_shell" and c.success:
                cmd = c.arguments.get("command", "")
                if cmd:
                    cmds.append(cmd)
        return cmds

    def has_failed_calls(self) -> bool:
        return any(not c.success for c in self.calls)

    def summary(self) -> dict:
        shell_calls = [
            c for c in self.calls
            if c.tool_name == "openclaw__run_shell"
        ]
        shell_exit_codes = [
            c.arguments.get("exit_code") for c in shell_calls
            if "exit_code" in c.arguments
        ]
        failed_shell_commands = [
            c.arguments.get("command", "") for c in shell_calls
            if c.arguments.get("exit_code", 0) not in (0, None)
        ]
        failed_calls = [
            {
                "tool_name": c.tool_name,
                "arguments": c.arguments,
                "error": c.error,
            }
            for c in self.calls if not c.success
        ]
        return {
            "total_calls": self.count(),
            "tools_used": list(self.tool_names_used()),
            "files_read": list(self.files_read()),
            "files_written": list(self.files_written()),
            "commands_run": self.commands_run(),
            "has_failures": self.has_failed_calls(),
            "failed_calls": failed_calls,
            "shell_calls": len(shell_calls),
            "shell_exit_codes": shell_exit_codes,
            "failed_shell_commands": failed_shell_commands,
            "read_file_count": len(self.files_read()),
            "write_file_count": len(self.files_written()),
            "total_duration_ms": round(
                sum(c.duration_ms for c in self.calls), 3
            ),
        }
