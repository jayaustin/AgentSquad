# operator_plan

```json
{
  "summary": "Short planning summary",
  "tasks": [
    {
      "task_id": "T-001",
      "title": "Task title",
      "description": "Detailed description",
      "owner": "technical-architect",
      "milestone": "M1",
      "status": "Todo",
      "dependencies": []
    }
  ],
  "initial_role_sequence": [
    "technical-architect",
    "development-engineer-python",
    "qa-manager"
  ]
}
```

`owner` rules:

- `owner` must be a valid non-operator role ID.
- `owner: "operator"` is forbidden.
- `initial_role_sequence` must not include `operator`.

# agent_result

```json
{
  "task_id": "T-001",
  "status": "In Validation",
  "summary": "What was completed",
  "updates": {
    "owner": "qa-manager"
  },
  "new_tasks": [],
  "handoff_request": {
    "target_role": "qa-manager",
    "reason": "Requires validation.",
    "requested_task_ids": [
      "T-001"
    ]
  },
  "notes_update": "Optional note text."
}
```

`agent_result` ownership rules:

- `updates.owner` may not be `operator`.
- Any task in `new_tasks` may not use `owner: "operator"`.
