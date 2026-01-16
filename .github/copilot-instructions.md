---
applyTo: "**/*.py"
---
# Code standard

## Code structure

- Simple and clear
- Type-safe, use `uv run ty check` and `uv run ruff check` to verify, avoid Any where possible, can add comment `# type: ignore` if type is not easily inferred

## Python environment

Using `uv`

Path: `${workspaceFolder}/.venv/bin/python`

## Error log

Always use `logging.exception()` to log exceptions with full traceback.

Don't print custom log messages - use structured logging.

## Documentation

Refer to the official documentation for detailed information on the API and usage examples.

- https://modelcontextprotocol.io/quickstart/server
- https://github.com/modelcontextprotocol/quickstart-resources
