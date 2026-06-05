"""Docker container lifecycle management for agent sessions."""

import io
import tarfile
import uuid
from pathlib import Path

import docker
from docker.errors import DockerException, NotFound, ImageNotFound

from .config import (
    CONTAINER_MEMORY_LIMIT,
    CONTAINER_CPU_LIMIT,
    DOCKER_NETWORK,
    READONLY_PATHS,
    ROLE_IMAGE_MAP,
)
from .models import SessionState, TaskConfig


class SessionManagerError(Exception):
    """Raised when session operations fail."""
    pass


class SessionManager:
    """Manages Docker containers for agent task sessions."""

    def __init__(self, tasks_dir: Path):
        self.tasks_dir = tasks_dir
        try:
            self.client = docker.from_env()
        except DockerException as e:
            raise SessionManagerError(
                f"Cannot connect to Docker daemon: {e}. "
                "Is Docker Desktop running?"
            )

    def _get_image_name(self, task_id: str) -> str:
        """Map task_id to Docker image name using ROLE_IMAGE_MAP."""
        prefix = task_id.split("_")[0]
        if prefix in ROLE_IMAGE_MAP:
            return ROLE_IMAGE_MAP[prefix]
        return f"openclaw-{prefix}"

    def _resolve_image(self, preferred: str) -> str:
        """Resolve Docker image with progressive fallback.

        Chain: preferred → openclaw-base → python:3.12-slim
        Returns the first image that exists locally.
        """
        # 1. Try the task-specific image
        try:
            self.client.images.get(preferred)
            return preferred
        except ImageNotFound:
            pass

        # 2. Try openclaw-base (has pytest + all common deps)
        try:
            self.client.images.get("openclaw-base")
            return "openclaw-base"
        except ImageNotFound:
            pass

        # 3. Fall back to bare Python — pytest will be installed post-create
        return "python:3.12-slim"

    def _install_pytest(self, container) -> None:
        """Install essential test deps in a bare Python container."""
        try:
            container.exec_run(
                "pip install --no-cache-dir --quiet "
                "pytest>=8.0 pyyaml>=6.0 pandas>=2.0 numpy>=1.24 "
                "beautifulsoup4>=4.12 lxml>=5.0 openpyxl>=3.1",
                workdir="/",
            )
        except Exception:
            pass  # Best effort — tests will fail gracefully if pip fails

    def create_session(self, team_id: str, task: TaskConfig) -> SessionState:
        """Create a new session with a Docker container for the task."""
        session_id = f"openclaw-{task.id}-{uuid.uuid4().hex[:8]}"
        image_name = self._get_image_name(task.id)

        # Resolve image with fallback chain:
        #   1. Task-specific image (e.g. openclaw-core05)
        #   2. openclaw-base (has pytest, pandas, numpy, beautifulsoup4, lxml)
        #   3. python:3.12-slim + auto-install pytest
        image_name = self._resolve_image(image_name)

        task_inputs_dir = Path(task.task_dir) / "inputs"

        # Create container
        try:
            container = self.client.containers.run(
                image=image_name,
                command="sleep infinity",
                detach=True,
                remove=True,
                name=session_id,
                mem_limit=CONTAINER_MEMORY_LIMIT,
                nano_cpus=int(float(CONTAINER_CPU_LIMIT) * 1e9),
                network=DOCKER_NETWORK,
                working_dir="/workspace",
            )
        except DockerException as e:
            raise SessionManagerError(f"Failed to create container: {e}")

        # If we fell back to bare python, install pytest now
        if image_name == "python:3.12-slim":
            self._install_pytest(container)

        # Copy task input files into the container's /workspace
        if task_inputs_dir.exists():
            self._copy_to_container(container, task_inputs_dir, "/workspace")

        # Mount hidden tests to /opt/verifier/ (invisible to agent via workspace tools)
        hidden_tests_dir = Path(task.task_dir) / "hidden_tests"
        if hidden_tests_dir.exists():
            self._copy_to_container(container, hidden_tests_dir, "/opt/verifier/hidden_tests")

        # Copy expected gold data for verifier
        expected_dir = Path(task.task_dir) / "expected"
        if expected_dir.exists():
            self._copy_to_container(container, expected_dir, "/opt/verifier/expected")

        # Copy verifier script
        verifier_dir = Path(task.task_dir) / "verifier"
        if verifier_dir.exists():
            self._copy_to_container(container, verifier_dir, "/opt/verifier/verifier")

        return SessionState(
            session_id=session_id,
            team_id=team_id,
            task_id=task.id,
            role=task.role,
            container_id=container.id,
            workspace_path="/workspace",
            time_budget_seconds=task.time_budget_minutes * 60,
        )

    def destroy_session(self, session: SessionState) -> None:
        """Stop and remove the container for a session."""
        if not session.container_id:
            return
        try:
            container = self.client.containers.get(session.container_id)
            container.stop(timeout=5)
        except NotFound:
            pass  # Already removed
        except DockerException as e:
            raise SessionManagerError(f"Failed to destroy container: {e}")

    def exec_command(self, session: SessionState, command: str,
                     workdir: str = "/workspace") -> tuple[str, str, int]:
        """Execute a command in the session's container.

        Returns (stdout, stderr, exit_code).
        """
        if not session.container_id:
            raise SessionManagerError("No container for this session")

        try:
            container = self.client.containers.get(session.container_id)
        except NotFound:
            raise SessionManagerError("Container no longer exists")

        result = container.exec_run(
            command,
            workdir=workdir,
            demux=True,
        )

        exit_code = result.exit_code
        stdout = ""
        stderr = ""

        if result.output:
            out, err = result.output
            stdout = out.decode("utf-8", errors="replace") if out else ""
            stderr = err.decode("utf-8", errors="replace") if err else ""

        return stdout, stderr, exit_code

    def read_file(self, session: SessionState, path: str) -> str:
        """Read a file from the container's workspace.

        Normalizes path to stay within /workspace.
        """
        safe_path = self._safe_path(path)
        stdout, stderr, exit_code = self.exec_command(
            session, f"cat {safe_path}"
        )
        if exit_code != 0:
            raise SessionManagerError(
                f"Cannot read {safe_path}: {stderr.strip()}"
            )
        return stdout

    def list_dir(self, session: SessionState, path: str = ".") -> list[dict]:
        """List directory contents in the container."""
        safe_path = self._safe_path(path)
        stdout, stderr, exit_code = self.exec_command(
            session, f"ls -la {safe_path}"
        )
        if exit_code != 0:
            raise SessionManagerError(
                f"Cannot list {safe_path}: {stderr.strip()}"
            )

        entries = []
        for line in stdout.strip().split("\n"):
            parts = line.split()
            if len(parts) < 9:
                continue
            name = " ".join(parts[8:])
            if name in (".", ".."):
                continue
            entries.append({
                "name": name,
                "type": "dir" if parts[0].startswith("d") else "file",
                "size": int(parts[4]) if parts[4].isdigit() else 0,
                "perms": parts[0],
            })
        return entries

    def write_file(self, session: SessionState, path: str, content: str) -> int:
        """Write content to a file in the container's workspace."""
        safe_path = self._safe_path(path)
        # Use a heredoc approach for safe content writing
        encoded = content.encode("utf-8")
        # Create a tar archive in memory and copy it
        tar_stream = io.BytesIO()
        with tarfile.open(fileobj=tar_stream, mode="w") as tar:
            # Remove /workspace/ prefix (lstrip is wrong - it strips chars, not prefix)
            arcname = safe_path.removeprefix("/workspace/")
            tarinfo = tarfile.TarInfo(name=arcname)
            tarinfo.size = len(encoded)
            tar.addfile(tarinfo, io.BytesIO(encoded))
        tar_stream.seek(0)

        try:
            container = self.client.containers.get(session.container_id)
        except NotFound:
            raise SessionManagerError("Container no longer exists")

        container.put_archive("/workspace", tar_stream)
        return len(encoded)

    def _safe_path(self, path: str) -> str:
        """Normalize path to stay within /workspace, preventing traversal."""
        normalized = path.strip()
        # Strip leading ./ if present
        if normalized.startswith("./"):
            normalized = normalized[2:]
        if normalized.startswith("/"):
            # If absolute, ensure it's under /workspace or /opt/verifier
            if normalized.startswith("/workspace/"):
                return normalized
            if normalized.startswith("/opt/verifier/"):
                return normalized
            # Prepend /workspace for other absolute paths
            return "/workspace/" + normalized.lstrip("/")
        # Relative path — under /workspace
        return "/workspace/" + normalized

    def _copy_to_container(self, container, src_dir: Path, dest_path: str) -> None:
        """Copy a local directory into the container at dest_path."""
        tar_stream = io.BytesIO()
        with tarfile.open(fileobj=tar_stream, mode="w") as tar:
            for f in src_dir.rglob("*"):
                if f.is_file():
                    arcname = str(f.relative_to(src_dir))
                    tar.add(f, arcname=arcname)
        tar_stream.seek(0)

        # Create destination directory and copy
        container.exec_run(f"mkdir -p {dest_path}")
        container.put_archive(dest_path, tar_stream)
