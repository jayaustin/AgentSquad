"""Role workspace log and notes persistence."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _safe_segment(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in {"-", "_"} else "-" for ch in value).strip("-")


def ensure_workspace(root: Path, role_id: str) -> Path:
    workspace_dir = root / "project" / "workspaces" / role_id
    runs_dir = workspace_dir / "runs"
    notes_path = workspace_dir / "notes.md"
    workspace_dir.mkdir(parents=True, exist_ok=True)
    runs_dir.mkdir(parents=True, exist_ok=True)
    if not notes_path.exists():
        notes_path.write_text(
            f"# {role_id} Notes\n\nProject-specific notes for `{role_id}`.\n",
            encoding="utf-8",
        )
    return workspace_dir


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True) + "\n")


def write_run_journal(
    root: Path,
    role_id: str,
    task_id: str,
    prompt_template: str,
    context_manifest: list[str],
    raw_output: str,
    parsed_result: dict,
    backlog_before: str,
    backlog_after: str,
    events: list[str] | None = None,
    event_type: str = "run_journal",
    summary: str = "",
    status: str = "",
    metadata: dict[str, Any] | None = None,
) -> Path:
    workspace = ensure_workspace(root, role_id)
    runs_dir = workspace / "runs"
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_task = _safe_segment(task_id or "no-task")
    path = runs_dir / f"{timestamp}-{safe_task}.md"

    event_lines = events or []
    lines: list[str] = []
    lines.append(f"# Run Journal: {role_id} / {task_id}")
    lines.append("")
    lines.append(f"- Timestamp (UTC): `{timestamp}`")
    lines.append(f"- Prompt Template: `{prompt_template}`")
    lines.append("")
    lines.append("## Context Manifest")
    lines.append("")
    for item in context_manifest:
        lines.append(f"- `{item}`")
    lines.append("")
    lines.append("## Events")
    lines.append("")
    if event_lines:
        for event in event_lines:
            lines.append(f"- {event}")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Backlog Snapshot (Before)")
    lines.append("")
    lines.append("```markdown")
    lines.append(backlog_before.rstrip())
    lines.append("```")
    lines.append("")
    lines.append("## Raw Model Output")
    lines.append("")
    lines.append("```text")
    lines.append(raw_output.rstrip())
    lines.append("```")
    lines.append("")
    lines.append("## Parsed Result")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps(parsed_result, indent=2, ensure_ascii=True))
    lines.append("```")
    lines.append("")
    lines.append("## Backlog Snapshot (After)")
    lines.append("")
    lines.append("```markdown")
    lines.append(backlog_after.rstrip())
    lines.append("```")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")

    event_summary = str(summary or parsed_result.get("summary") or "Run journal written.").strip()
    event_status = str(status or parsed_result.get("status") or "").strip()
    run_path = path.relative_to(root).as_posix()
    base_metadata: dict[str, Any] = {
        "prompt_template": prompt_template,
        "context_manifest": list(context_manifest),
        "events": list(event_lines),
    }
    if metadata:
        base_metadata.update(metadata)
    payload = {
        "ts_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "role_id": role_id,
        "task_id": task_id,
        "event_type": event_type,
        "summary": event_summary,
        "run_journal_path": run_path,
        "status": event_status,
        "metadata": base_metadata,
    }
    _append_jsonl(root / "project" / "state" / "activity-log.jsonl", payload)
    _append_jsonl(workspace / "activity.jsonl", payload)
    return path
