"""Pydantic data models for tasks, sessions, and scores."""

from datetime import datetime
from pathlib import Path
from typing import Optional
from enum import Enum

from pydantic import BaseModel, Field


class TaskRole(str, Enum):
    SOFTWARE_ENGINEER = "software_engineer"
    DATA_ANALYST = "data_analyst"
    UI_DESIGNER = "ui_designer"
    TECHNICAL_WRITER = "technical_writer"
    LOCALIZATION = "localization"
    DIGITAL_HUMANITIES = "digital_humanities"


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class TaskConfig(BaseModel):
    """Loaded from task.yaml."""
    id: str
    role: TaskRole
    difficulty: Difficulty = Difficulty.MEDIUM
    time_budget_minutes: int = 12
    allowed_tools: list[str] = Field(default_factory=list)
    required_outputs: list[str] = Field(default_factory=list)
    forbidden_actions: list[str] = Field(default_factory=list)
    scoring: dict = Field(default_factory=dict)

    # Path to task directory (set at load time, not in yaml)
    task_dir: str = ""


class ToolCall(BaseModel):
    """Record of a single MCP tool invocation."""
    tool_name: str
    arguments: dict = Field(default_factory=dict)
    timestamp: float  # unix epoch seconds
    success: bool = True
    error: Optional[str] = None
    duration_ms: float = 0.0


class SessionState(BaseModel):
    """Runtime state for one agent session."""
    session_id: str
    team_id: str
    task_id: str
    role: TaskRole
    container_id: Optional[str] = None
    workspace_path: str = "/workspace"
    started_at: datetime = Field(default_factory=datetime.now)
    time_budget_seconds: int = 720
    tool_calls: list[ToolCall] = Field(default_factory=list)
    submitted: bool = False
    pilot_run_id: str = ""
    agent_id: str = ""
    model_id: str = ""
    skill_variant: str = "control"
    trial_index: int = 0
    seed: str = ""


class ScoreResult(BaseModel):
    """Final score after submit()."""
    task_id: str
    role: str
    total_score: float = 0.0
    completion_score: float = 0.0
    constraint_score: float = 0.0
    process_score: float = 0.0
    communication_score: float = 0.0
    verifier_passed: bool = False
    failed_checks: list[str] = Field(default_factory=list)
    safety_violations: list[str] = Field(default_factory=list)
    time_seconds: int = 0
    tool_calls: int = 0
    trace_summary: dict = Field(default_factory=dict)
    pilot_metadata: dict = Field(default_factory=dict)
