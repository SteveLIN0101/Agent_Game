"""The Red Dust world: live visible_state + static inputs + a replay trajectory.

Tools mutate the ``World``; the verifier reads it.  Everything the audience sees
during replay (the beats, the state deltas, the produced artifacts) lives here.
"""

from copy import deepcopy
from typing import Any


class World:
    def __init__(self, state: dict | None = None, inputs: dict | None = None):
        self.state: dict = deepcopy(state) if state else {}
        self.inputs: dict = inputs or {}
        self.events: list[dict] = []
        self.artifacts: dict[str, Any] = {}
        self.security_log: list[str] = []

    # --- trajectory ------------------------------------------------------
    def record(self, tool: str, args: dict | None = None,
               beat: str | None = None, delta: dict | None = None) -> None:
        """Record one tool invocation as a replayable beat, applying any delta."""
        if delta:
            self.apply_delta(**delta)
        self.events.append({
            "tool": tool,
            "args": args or {},
            "beat": beat,
            "delta": delta or {},
        })

    def apply_delta(self, **kv: Any) -> None:
        """Relative numeric change to state fields (e.g. battery=-2)."""
        for key, change in kv.items():
            cur = self.state.get(key)
            if isinstance(cur, (int, float)) and isinstance(change, (int, float)):
                self.state[key] = cur + change
            else:
                self.state[key] = change

    def used_tool(self, name: str) -> bool:
        return any(e["tool"] == name for e in self.events)

    def tool_count(self, name: str) -> int:
        return sum(1 for e in self.events if e["tool"] == name)

    # --- artifacts -------------------------------------------------------
    def set_artifact(self, name: str, value: Any) -> None:
        self.artifacts[name] = value

    def artifact(self, name: str, default: Any = None) -> Any:
        return self.artifacts.get(name, default)

    # --- state helpers ---------------------------------------------------
    def set(self, key: str, value: Any) -> None:
        self.state[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self.state.get(key, default)

    def log_security(self, message: str) -> None:
        self.security_log.append(message)
