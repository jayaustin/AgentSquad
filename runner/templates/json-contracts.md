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

