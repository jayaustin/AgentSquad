"""Kiro host adapter stub."""

from .base import AdapterError, BaseAdapter


class KiroAdapter(BaseAdapter):
    """Stub adapter for Kiro integration."""

    adapter_id = "kiro"

    def invoke(self, command: str, prompt: str) -> str:
        raise AdapterError(
            "Kiro adapter is not implemented yet. "
            "Keep primary_adapter=codex or implement runner/adapters/kiro.py."
        )

