"""Host adapters for non-API assistant invocation."""

from .base import AdapterError, BaseAdapter
from .codex import CodexAdapter
from .kiro import KiroAdapter
from .roo import RooAdapter


def build_adapter(name: str) -> BaseAdapter:
    lowered = (name or "").strip().lower()
    if lowered == "codex":
        return CodexAdapter()
    if lowered == "roo":
        return RooAdapter()
    if lowered == "kiro":
        return KiroAdapter()
    raise AdapterError(f"Unsupported adapter '{name}'.")

