# Backlog Governance

## Canonical Header

`| Task ID | Title | Description | Owner | Milestone | Status | Dependencies |`

## Rules

1. `Owner` is a single role ID from the role registry.
2. `Status` must be one of: `Todo`, `In Progress`, `Blocked`, `In Validation`, `Done`.
3. `Dependencies` is a comma-separated list of task IDs or empty.
4. Operator and non-operator roles can create and update tasks via machine-validated contracts.
5. Task selection policy is dependency-first, FIFO second.

