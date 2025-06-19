<!-- @format -->

# Canonical MCP Server (Official SDK)

A minimal, canonical Model Context Protocol server for task management, fully compliant, and ready for LM Studio, Claude, Cursor, and more.

## How to Run

```bash
# Install dependencies
uv sync

# Run the server
uv run server.py
```

## Endpoints / Tools

- `get-tasks`: List all tasks
- `add-task`: Add a new task
- `set-task-status`: Change task status
- `get-task`: Get task details by ID
- `next-task`: Get the next pending task
- `update-task`: Update task title/description

## Integration

- Add your server URL (`http://localhost:8080`) in LM Studio, Claude, Cursor, etc.
- Tools are auto-discovered by MCP clients.

## Extending

- To support resources or prompts, see the [official docs](https://modelcontextprotocol.io/quickstart/server).
- Swap `tasks_db.py` for a persistent DB (e.g., SQLite, Postgres) for production.

## Setup from Scratch

```bash
# Initialize new project with uv
uv init task-manager-server
cd task-manager-server

# Add dependencies
uv add mcp pydantic

# Run the server
uv run server.py
```

## Best Practices

- Use UV for Python dependency management (canonical MCP approach)
- Follow [MCP architecture concepts](https://modelcontextprotocol.io/docs/concepts/architecture).
- Use Pydantic for schema validation and strong typing.
- Handle errors and input validation at every tool method.
- Log actions and errors in production environments.
- Add authentication (token or basic auth) if exposing outside localhost.

---

You now have a **production-ready, canonical MCP Python server** that is discoverable and usable by all MCP-compliant clients.

---

For step-by-step integration with LM Studio, see:

- [LM Studio: MCP Plugin Docs](https://lmstudio.ai/)
- [Official MCP Client/Server List](https://modelcontextprotocol.io/clients)
