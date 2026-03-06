You are executing a role task in AgentSquad.

Return ONLY valid JSON following the `agent_result` contract.

Important constraints:

- Do not assign or reassign any task owner to `operator`.
- Any new tasks in `new_tasks` must be owned by non-operator roles.
- Add `decision_log` with meaningful implementation/validation decisions.
- Add `unexpected_events` when you hit anomalies, uncertainty, or blockers.
- If you need human input, include `human_feedback`.
- If you need to pass guidance/questions to another role, include `role_feedback`.

## Task

{{TASK_JSON}}

## Current Backlog

{{BACKLOG_MARKDOWN}}

## Context Manifest

{{CONTEXT_MANIFEST}}

## Loaded Context

{{CONTEXT_TEXT}}

## JSON Contract Reference

{{JSON_CONTRACTS}}
