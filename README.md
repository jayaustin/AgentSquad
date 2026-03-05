# AgentSquad v1

AgentSquad is a non-API orchestration framework for IDE-based agent workflows.
It separates global framework assets from project-specific state, and runs a
sequential, operator-mediated execution loop.

## Core Ideas

- Global framework assets live under `steering/`, `agents/`, and `superpowers/`.
- Project-specific assets live under `project/`.
- `Operator` is the only role that interfaces directly with the human request.
- Roles execute sequentially with strict context load order:
  `steering -> role -> project -> role-override`.
- Backlog is the source of truth for work ownership and status.

## CLI

Run commands from repository root:

```bash
python -m runner.orchestrator init
python -m runner.orchestrator validate
python -m runner.orchestrator run --request "your request"
python -m runner.orchestrator step
python -m runner.orchestrator resume
```

## Host Adapter

This framework is API-free. It invokes a local assistant command configured in
`project/config/project.yaml` at:

- `host.primary_adapter` (`codex`, `roo`, `kiro`)
- `host.adapter_command` (shell command that reads prompt input and writes JSON)

The runner passes prompt data through:

- `STDIN`
- `AGENTSQUAD_PROMPT` environment variable

## Validation Guarantees

- Role files exist for every enabled role.
- Role frontmatter includes required contract keys.
- Referenced superpower IDs are valid.
- Backlog header matches the required schema.
- Project config matches required keys and fixed execution policies.

