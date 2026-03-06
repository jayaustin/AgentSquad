"""Cursor host adapter stub."""

from .base import AdapterError, BaseAdapter


class CursorAdapter(BaseAdapter):
    """Stub adapter for Cursor Agent integration."""

    adapter_id = "cursor"

    def invoke(self, command: str, prompt: str) -> str:
        raise AdapterError(
            "Cursor adapter is not implemented yet. "
            "Keep host.primary_adapter=codex or implement runner/adapters/cursor.py."
        )
