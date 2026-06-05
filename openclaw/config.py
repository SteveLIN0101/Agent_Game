"""Environment-based configuration."""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = Path(os.getenv("OPENCLAW_TASKS_DIR", PROJECT_ROOT / "tasks"))

# Auth
AUTH_TOKEN = os.getenv("OPENCLAW_AUTH_TOKEN", "openclaw-dev-token")

# Docker
DOCKER_BASE_IMAGE = os.getenv("OPENCLAW_DOCKER_BASE", "openclaw-base:latest")
DOCKER_REGISTRY = os.getenv("OPENCLAW_DOCKER_REGISTRY", "")  # optional prefix
DOCKER_NETWORK = os.getenv("OPENCLAW_DOCKER_NETWORK", "openclaw-net")
CONTAINER_MEMORY_LIMIT = os.getenv("OPENCLAW_CONTAINER_MEMORY", "512m")
CONTAINER_CPU_LIMIT = os.getenv("OPENCLAW_CONTAINER_CPU", "1.0")

# Budget defaults (per-task overrides in task.yaml)
DEFAULT_TIME_BUDGET_SECONDS = int(os.getenv("OPENCLAW_DEFAULT_TIME_BUDGET", "720"))  # 12 min

# Shell whitelist
SHELL_WHITELIST = [
    "pytest", "python", "python3",
    "ls", "cat", "head", "tail", "wc",
    "grep", "find",
    "git", "diff", "patch",
    "node", "npm", "npx",
    "echo", "sort", "uniq", "cut",
    "cd", "pwd", "mkdir", "cp", "mv", "touch",
    "sed", "awk", "tr",
]

# Forbidden commands (even if they match whitelist prefix)
SHELL_FORBIDDEN = [
    "rm ", "rmdir", "chmod", "chown", "chattr",
    "curl", "wget", "nc ", "telnet", "ssh",
    "pip install", "pip3 install", "apt", "yum",
    "kill", "reboot", "shutdown",
    "mount", "umount",
    "> /", ">> /",  # redirects to root
]

# Paths the agent cannot write to
READONLY_PATHS = ["tests/", "expected/", "/opt/verifier/"]

# Paths the agent cannot inspect directly. Visible tests under tests/ remain
# readable, but evaluator materials and hidden tests must only be used by
# submit-time verifier code.
HIDDEN_EVAL_PATHS = ["expected/", "/opt/", "/opt/verifier/"]

# Verifier library (shared utilities copied into task verifier dirs)
VERIFIER_LIB_DIR = PROJECT_ROOT / "tasks" / "verifier_lib"

# Scoring weights
SCORING = {
    "completion": 0.60,
    "constraint": 0.20,
    "process": 0.15,
    "communication": 0.05,
}

# Docker image mapping per role prefix
ROLE_IMAGE_MAP = {
    "core01": "openclaw-core01",
    "core02": "openclaw-core02",
    "core03": "openclaw-core03",
    "core04": "openclaw-core04",
    "core05": "openclaw-core05",
    "core06": "openclaw-core06",
}
