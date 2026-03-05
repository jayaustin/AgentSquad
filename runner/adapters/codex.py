"""Codex host adapter."""

from .base import BaseAdapter


class CodexAdapter(BaseAdapter):
    """Adapter for Codex-style local host execution."""

    adapter_id = "codex"

