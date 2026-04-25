# MonitorDocs Architecture (initial)

This file captures the initial architecture decisions for the MonitorDocs project.

- Web API: FastAPI service located at `MonitorDocs/webapp` for quick prototyping and agent integrations.
- Agent knowledge: filesystem-first YAML storage under `MonitorDocs/agents/knowledge` for easy review and versioning.
- Local DB: a single-file SQLite database `MonitorDocs/agents.db` is used for structured reads/writes by the API and agents.

Reference: see [MonitorDocs/placeholder.md](MonitorDocs/placeholder.md) for project intent.
