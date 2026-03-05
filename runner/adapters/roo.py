"""Roo host adapter stub."""

from .base import AdapterError, BaseAdapter


class RooAdapter(BaseAdapter):
    """Stub adapter for Roo integration."""

    adapter_id = "roo"

    def invoke(self, command: str, prompt: str) -> str:
        raise AdapterError(
            "Roo adapter is not implemented yet. "
            "Keep primary_adapter=codex or implement runner/adapters/roo.py."
        )

