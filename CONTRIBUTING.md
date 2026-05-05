# Contributing

Thank you for your interest in contributing to recombee-mcp!

## Setup

```bash
# Clone
git clone https://github.com/martinspacek/recombee-mcp.git
cd recombee-mcp

# Install uv (if not already installed)
# macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows:
winget install astral-sh.uv

# Install dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install

# Copy environment template
cp .env.example .env
```

## Development Workflow

1. Create a feature branch: `git checkout -b feat/my-feature`
2. Make changes and ensure checks pass:
   ```bash
   uv run ruff check .
   uv run ruff format --check .
   uv run mypy src/
   uv run pytest
   ```
3. Commit using [Conventional Commits](https://www.conventionalcommits.org/):
   `feat(tools): add my_new_tool`
4. Open a Pull Request against `main`

## Commit Message Format

```
type(scope): subject
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `security`

## Plans Convention

Before non-trivial work, create a plan in `.claude-plans/`. See `.claude-plans/README.md`.

## Claude Code Users

If using Claude Code with this project:

1. Optionally set `CONTEXT7_API_KEY` in your shell (free key from https://context7.com/dashboard)
2. Personal overrides go in `.claude/settings.local.json` (gitignored)

## Running Tests

```bash
# Unit tests (no credentials needed)
uv run pytest tests/unit/

# Integration tests (requires sandbox credentials in .env)
RECOMBEE_INTEGRATION_DB_ID=... RECOMBEE_INTEGRATION_TOKEN=... uv run pytest tests/integration/
```
