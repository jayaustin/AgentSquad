"""Claude Code host adapter stub."""

from .base import AdapterError, BaseAdapter


class ClaudeCodeAdapter(BaseAdapter):
    """Stub adapter for Claude Code integration."""

    adapter_id = "claude-code"

    def invoke(self, command: str, prompt: str) -> str:
        raise AdapterError(
            "Claude Code adapter is not implemented yet. "
            "Keep host.primary_adapter=codex or implement runner/adapters/claude_code.py."
        )
