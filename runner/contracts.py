"""JSON contract parsing and validation."""

from __future__ import annotations

import json
import re
from typing import Any


TASK_REQUIRED_FIELDS = (
    "task_id",
    "title",
    "description",
    "owner",
    "milestone",
    "status",
    "dependencies",
)


class ContractError(ValueError):
    """Raised when output contract is invalid."""


def _parse_scalar_string(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _normalize_dependencies(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        raw = [part.strip() for part in value.split(",")]
        return [item for item in raw if item]
    raise ContractError("dependencies must be a list or comma-separated string.")


def _extract_json_text(raw_text: str) -> str:
    stripped = (raw_text or "").strip()
    if not stripped:
        raise ContractError("Empty response; JSON contract required.")

    fenced = re.search(r"```(?:json)?\s*(.*?)```", stripped, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        return fenced.group(1).strip()

    first_brace = stripped.find("{")
    last_brace = stripped.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        return stripped[first_brace : last_brace + 1]
    return stripped


def parse_json_payload(raw_text: str) -> dict[str, Any]:
    """Parse JSON payload from model output."""
    payload_text = _extract_json_text(raw_text)
    try:
        parsed = json.loads(payload_text)
    except json.JSONDecodeError as exc:
        raise ContractError(f"Invalid JSON payload: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ContractError("JSON payload must be an object.")
    return parsed


def _validate_task(task: Any, allowed_statuses: set[str], known_roles: set[str]) -> dict[str, Any]:
    if not isinstance(task, dict):
        raise ContractError("Task entry must be an object.")
    missing = [field for field in TASK_REQUIRED_FIELDS if field not in task]
    if missing:
        raise ContractError(f"Task missing required fields: {', '.join(missing)}")

    normalized = {
        "task_id": _parse_scalar_string(task["task_id"]),
        "title": _parse_scalar_string(task["title"]),
        "description": _parse_scalar_string(task["description"]),
        "owner": _parse_scalar_string(task["owner"]),
        "milestone": _parse_scalar_string(task["milestone"]),
        "status": _parse_scalar_string(task["status"]),
        "dependencies": _normalize_dependencies(task["dependencies"]),
    }

    if not normalized["task_id"]:
        raise ContractError("task_id cannot be empty.")
    if normalized["owner"] not in known_roles:
        raise ContractError(f"Unknown task owner '{normalized['owner']}'.")
    if normalized["status"] not in allowed_statuses:
        raise ContractError(
            f"Invalid task status '{normalized['status']}'. "
            f"Allowed: {sorted(allowed_statuses)}"
        )
    return normalized


def validate_operator_plan(
    payload: dict[str, Any], allowed_statuses: list[str], known_roles: set[str]
) -> dict[str, Any]:
    """Validate and normalize operator_plan contract."""
    if "tasks" not in payload or not isinstance(payload["tasks"], list):
        raise ContractError("operator_plan requires a tasks list.")
    if "initial_role_sequence" not in payload or not isinstance(
        payload["initial_role_sequence"], list
    ):
        raise ContractError("operator_plan requires initial_role_sequence list.")

    status_set = set(allowed_statuses)
    normalized_tasks = [_validate_task(task, status_set, known_roles) for task in payload["tasks"]]

    normalized_sequence = [str(role).strip() for role in payload["initial_role_sequence"] if str(role).strip()]
    unknown_roles = [role for role in normalized_sequence if role not in known_roles]
    if unknown_roles:
        raise ContractError(f"initial_role_sequence contains unknown roles: {unknown_roles}")

    return {
        "type": "operator_plan",
        "summary": _parse_scalar_string(payload.get("summary", "")),
        "tasks": normalized_tasks,
        "initial_role_sequence": normalized_sequence,
    }


def validate_agent_result(
    payload: dict[str, Any], allowed_statuses: list[str], known_roles: set[str]
) -> dict[str, Any]:
    """Validate and normalize agent_result contract."""
    required = ("task_id", "status")
    missing = [field for field in required if field not in payload]
    if missing:
        raise ContractError(f"agent_result missing required fields: {', '.join(missing)}")

    status = _parse_scalar_string(payload["status"])
    status_set = set(allowed_statuses)
    if status not in status_set:
        raise ContractError(
            f"Invalid agent_result status '{status}'. Allowed: {sorted(status_set)}"
        )

    updates = payload.get("updates", {})
    if updates is None:
        updates = {}
    if not isinstance(updates, dict):
        raise ContractError("agent_result updates must be an object.")

    new_tasks_raw = payload.get("new_tasks", [])
    if new_tasks_raw is None:
        new_tasks_raw = []
    if not isinstance(new_tasks_raw, list):
        raise ContractError("agent_result new_tasks must be a list.")
    new_tasks = [_validate_task(task, status_set, known_roles) for task in new_tasks_raw]

    handoff_request = payload.get("handoff_request")
    normalized_handoff = None
    if handoff_request is not None:
        if not isinstance(handoff_request, dict):
            raise ContractError("handoff_request must be an object.")
        target_role = _parse_scalar_string(handoff_request.get("target_role", ""))
        reason = _parse_scalar_string(handoff_request.get("reason", ""))
        requested_task_ids = _normalize_dependencies(handoff_request.get("requested_task_ids", []))
        if not target_role:
            raise ContractError("handoff_request.target_role cannot be empty.")
        if target_role not in known_roles:
            raise ContractError(f"handoff_request target role '{target_role}' is unknown.")
        if not reason:
            raise ContractError("handoff_request.reason cannot be empty.")
        normalized_handoff = {
            "target_role": target_role,
            "reason": reason,
            "requested_task_ids": requested_task_ids,
        }

    return {
        "type": "agent_result",
        "task_id": _parse_scalar_string(payload["task_id"]),
        "status": status,
        "summary": _parse_scalar_string(payload.get("summary", "")),
        "updates": updates,
        "new_tasks": new_tasks,
        "handoff_request": normalized_handoff,
        "notes_update": _parse_scalar_string(payload.get("notes_update", "")),
    }

