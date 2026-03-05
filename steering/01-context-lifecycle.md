# Context Lifecycle

## Mandatory Load Order

1. `steering/*.md` (sorted lexicographically)
2. `agents/roles/<role-id>/agent-role.md`
3. `project/context/project-context.md`
4. `project/context/role-overrides/<role-id>.md` (if present)

## Invariants

1. A role invocation must record the full load manifest before execution.
2. Existing active role context must be unloaded before loading a new role.
3. If any required context file is missing, execution halts immediately.
4. Context switches must be logged to role run journals and orchestration state.

