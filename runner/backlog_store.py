"""Markdown backlog parsing and persistence."""

from __future__ import annotations

from pathlib import Path
from typing import Any


BACKLOG_COLUMNS = (
    "Task ID",
    "Title",
    "Description",
    "Owner",
    "Milestone",
    "Status",
    "Dependencies",
)

BACKLOG_HEADER = "| " + " | ".join(BACKLOG_COLUMNS) + " |"
BACKLOG_SEPARATOR = "| " + " | ".join(["---"] * len(BACKLOG_COLUMNS)) + " |"


class BacklogError(ValueError):
    """Raised when backlog format is invalid."""


def sanitize_cell(value: Any) -> str:
    return str(value or "").replace("|", "/").strip()


def _dependencies_to_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    raw = [part.strip() for part in str(value).split(",")]
    return [item for item in raw if item]


def normalize_task(task: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": sanitize_cell(task.get("task_id")),
        "title": sanitize_cell(task.get("title")),
        "description": sanitize_cell(task.get("description")),
        "owner": sanitize_cell(task.get("owner")),
        "milestone": sanitize_cell(task.get("milestone")),
        "status": sanitize_cell(task.get("status")),
        "dependencies": _dependencies_to_list(task.get("dependencies")),
    }


def read_backlog(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        return []
    if lines[0].strip() != BACKLOG_HEADER:
        raise BacklogError("Backlog header does not match required schema.")
    if len(lines) >= 2 and not lines[1].strip().startswith("|"):
        raise BacklogError("Backlog separator row is missing or invalid.")
    rows: list[dict[str, Any]] = []
    for line in lines[2:]:
        stripped = line.strip()
        if not stripped or not stripped.startswith("|"):
            continue
        parts = [part.strip() for part in stripped.strip("|").split("|")]
        if len(parts) != len(BACKLOG_COLUMNS):
            raise BacklogError(f"Invalid backlog row: {line}")
        rows.append(
            normalize_task(
                {
                    "task_id": parts[0],
                    "title": parts[1],
                    "description": parts[2],
                    "owner": parts[3],
                    "milestone": parts[4],
                    "status": parts[5],
                    "dependencies": parts[6],
                }
            )
        )
    return rows


def render_backlog(tasks: list[dict[str, Any]]) -> str:
    lines = [BACKLOG_HEADER, BACKLOG_SEPARATOR]
    for task in tasks:
        normalized = normalize_task(task)
        dep_text = ", ".join(normalized["dependencies"])
        lines.append(
            "| "
            + " | ".join(
                [
                    normalized["task_id"],
                    normalized["title"],
                    normalized["description"],
                    normalized["owner"],
                    normalized["milestone"],
                    normalized["status"],
                    dep_text,
                ]
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def write_backlog(path: Path, tasks: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_backlog(tasks), encoding="utf-8")


def upsert_tasks(existing: list[dict[str, Any]], incoming: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized_existing = [normalize_task(item) for item in existing]
    by_id = {task["task_id"]: task for task in normalized_existing}
    order = [task["task_id"] for task in normalized_existing]
    for task in incoming:
        normalized = normalize_task(task)
        task_id = normalized["task_id"]
        if task_id in by_id:
            by_id[task_id].update(normalized)
        else:
            by_id[task_id] = normalized
            order.append(task_id)
    return [by_id[task_id] for task_id in order]


def index_by_task_id(tasks: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {task["task_id"]: task for task in tasks}


def dependencies_satisfied(task: dict[str, Any], task_index: dict[str, dict[str, Any]]) -> bool:
    for dependency in task.get("dependencies", []):
        dep_task = task_index.get(dependency)
        if not dep_task or dep_task.get("status") != "Done":
            return False
    return True


def all_done(tasks: list[dict[str, Any]]) -> bool:
    return all(task.get("status") == "Done" for task in tasks)


def remaining_not_done(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [task for task in tasks if task.get("status") != "Done"]


def select_next_task(
    tasks: list[dict[str, Any]],
    enabled_roles: set[str],
    role_priority: list[str] | None = None,
) -> dict[str, Any] | None:
    role_priority = role_priority or []
    role_rank = {role_id: index for index, role_id in enumerate(role_priority)}
    task_index = index_by_task_id(tasks)
    executable: list[tuple[int, int, dict[str, Any]]] = []

    for row_index, task in enumerate(tasks):
        status = task.get("status")
        owner = task.get("owner")
        if status not in {"Todo", "In Progress"}:
            continue
        if owner not in enabled_roles:
            continue
        if not dependencies_satisfied(task, task_index):
            continue
        rank = role_rank.get(owner, len(role_rank))
        executable.append((rank, row_index, task))

    if not executable:
        return None
    executable.sort(key=lambda item: (item[0], item[1]))
    return executable[0][2]

