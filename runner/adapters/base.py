"""Adapter base types for host invocation."""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass


class AdapterError(RuntimeError):
    """Raised when host adapter invocation fails."""


@dataclass(frozen=True)
class AdapterInvocation:
    """Normalized invocation payload."""

    adapter_id: str
    command: str
    prompt: str


class BaseAdapter:
    """Base adapter that invokes a local assistant command."""

    adapter_id = "base"

    def invoke(self, command: str, prompt: str) -> str:
        if not command or "REPLACE_WITH_LOCAL_ASSISTANT_COMMAND" in command:
            raise AdapterError(
                "host.adapter_command is not configured. "
                "Set project/config/project.yaml to a working local command."
            )
        env = os.environ.copy()
        env["AGENTSQUAD_PROMPT"] = prompt
        completed = subprocess.run(
            command,
            input=prompt,
            capture_output=True,
            text=True,
            shell=True,
            env=env,
            check=False,
        )
        if completed.returncode != 0:
            stderr = (completed.stderr or "").strip()
            raise AdapterError(
                f"{self.adapter_id} invocation failed with exit code "
                f"{completed.returncode}: {stderr}"
            )
        output = (completed.stdout or "").strip()
        if not output:
            raise AdapterError(f"{self.adapter_id} invocation returned empty output.")
        return output

