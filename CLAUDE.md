# Recombee MCP Server — Project Bootstrap

> **For Claude Code:** This file is the entry-point brief for a brand-new project. The folder
> is currently empty except for this document. **Do not start coding immediately.** Read this
> file end-to-end, then follow §11 ("Your first actions").

---

## 1. Mission

Build a **production-grade, open-source Python MCP (Model Context Protocol) server**
that wraps the [Recombee](https://docs.recombee.com/) recommendation engine API,
so AI agents (primarily Claude Code and Claude Desktop) can analyze, debug, and
tune a live Recombee deployment through natural-language conversation.

The primary user is an e-commerce consultant operating Recombee for **Potten & Pannen**,
a Czech/Slovak premium kitchenware e-shop. Typical workflows the server must enable:

- Inspect any item's properties and ask Claude to spot data-quality issues
- Request recommendations for a synthetic user/scenario combo and have Claude reason
  about why the result looks the way it does
- Audit scenario configuration, filters, and boosters to identify gaps
- Compare scenario outputs A/B and have Claude propose ReQL refinements
- Diagnose cold-start behavior for new items or low-traffic categories

This is **not** a one-off script. It is a long-lived project intended to be published
on GitHub under a permissive license, with proper packaging, tests, CI, docs, and
versioning. Treat every file you create accordingly.

---

## 2. Read this first

A few rules that apply to **every** action you take in this project:

1. **Plans live in `.claude-plans/`.** Before any non-trivial change (new feature,
   refactor, dependency upgrade, architectural decision) you write a numbered plan
   markdown file there. Format: `NN-short-slug.md` (e.g. `01-initial-implementation.md`,
   `02-add-write-tools.md`). The plan is reviewed by the human before execution.
2. **No destructive Recombee operations are ever exposed as tools.** See §4.2.
3. **Every tool you add gets at least one happy-path test and one error-path test.**
4. **Conventional Commits.** Every commit message follows
   `type(scope): subject`, e.g. `feat(tools): add recommend_to_item tool`.
5. **Never commit secrets.** API tokens go in `.env` (gitignored) and are loaded
   via `pydantic-settings`. Provide `.env.example` with placeholder values.
6. **When in doubt about a library API, use Context7** (see §7.4). Don't rely on
   training-data memory for SDK signatures — fetch current docs.
7. **Push back on the human if a request would degrade the project.** Saying "no,
   here's why, here's a better approach" is a feature, not a bug.

---

## 3. Stack & decisions

### 3.1 Python toolchain

- **Python:** Latest stable CPython (verify with `python --version` against
  https://www.python.org/downloads/ — at the time this brief is written, that should
  be 3.13 or 3.14). Pin a minimum in `pyproject.toml` of `>=3.12` so we get modern
  generics syntax (`list[int]`, PEP 695 type aliases) and `tomllib` in stdlib.
- **Package & env manager:** `uv` (Astral). One tool replaces pip, virtualenv,
  pyenv, pip-tools, poetry. Use `uv add` / `uv remove` / `uv sync` / `uv run`.
  `uv.lock` is committed to the repo. No `requirements.txt`, no `setup.py`,
  no `setup.cfg`.
- **Build backend:** `hatchling` (declared in `pyproject.toml`). Hatchling is
  uv-friendly, simple, and the de-facto modern default.

### 3.2 MCP framework

- **`fastmcp`** (latest 2.x or 3.x — check current major). Decorator-driven,
  generates JSON Schema from Python type hints, supports stdio and Streamable
  HTTP transports, has built-in dev inspector.
- Default transport: **stdio**. The server is spawned as a subprocess by the MCP
  host (Claude Desktop, Claude Code). HTTP transport is supported as a config flag
  for future remote deployment but is not the primary path.
- **Logging discipline:** under stdio transport, **never** write to stdout from
  application code — it corrupts the JSON-RPC stream. Configure the root logger
  to write to stderr and (optionally) a rotating file. Use `structlog` for
  structured records.

### 3.3 Recombee SDK

- **`recombee-api-client`** (official Python SDK). Wraps the REST API; every
  request type (`RecommendItemsToUser`, `GetItemValues`, `Batch`, etc.) is a class.
- The SDK is **synchronous**. Wrap calls in `anyio.to_thread.run_sync` if and only
  if FastMCP forces async at the tool-handler level. (FastMCP supports sync handlers
  natively, so async wrapping is usually unnecessary — verify against current docs.)
- All SDK errors must be caught and translated into MCP-friendly tool errors
  (clear message, no stack trace leaked to the model).

### 3.4 Code quality

- **Linter + formatter:** `ruff` (Astral). Replaces black, isort, flake8, pylint,
  pyupgrade, pydocstyle. Single tool, single config in `pyproject.toml` under
  `[tool.ruff]`. Use a strong-but-pragmatic preset:
  - Enable `E`, `W`, `F`, `I`, `B`, `UP`, `SIM`, `PTH`, `RUF`, `S` (flake8-bandit
    for security), `N`, `D` (pydocstyle, but only for the public API), `ANN`
    (type-annotation enforcement).
  - Line length: 100.
  - Format on save (configure in `.vscode/settings.json` if VS Code is detected).
- **Type checker:** `mypy` in **strict mode** (`strict = true` in pyproject).
  Watch the `ty` project (Astral's type checker) — once it hits stable, plan a
  migration in a future `.claude-plans/` entry. Don't migrate prematurely.
- **Security scan:** `pip-audit` and ruff's `S` rules in CI.
- **Pre-commit hooks** (`pre-commit` framework): ruff lint, ruff format, mypy,
  conventional-commit message check, trailing-whitespace/EOF fixers. Hooks run on
  staged files only — fast feedback.

### 3.5 Testing

- **`pytest`** as the runner. **`pytest-cov`** for coverage. **`pytest-mock`**
  for the `mocker` fixture. **`pytest-asyncio`** only if any async code lands.
- **Recombee SDK is mocked** in unit tests — never hit the real API in `tests/unit/`.
  Use `mocker.patch.object(client, "send", ...)` style.
- **Integration tests** (`tests/integration/`) hit a real Recombee sandbox database.
  Skip-by-default unless `RECOMBEE_INTEGRATION_DB_ID` env var is set. CI runs them
  on `main` branch only, gated on a repository secret.
- **Coverage target:** 90% for `src/recombee_mcp/tools/` and `src/recombee_mcp/server.py`.
  60% acceptable for plumbing modules. Coverage report uploaded to CI artifacts.
- Test names follow `test_<unit>_<scenario>_<expectation>` — e.g.
  `test_recommend_to_user_with_invalid_scenario_raises_value_error`.

### 3.6 CI/CD

GitHub Actions, three workflows:

- **`.github/workflows/ci.yml`** — runs on every push and PR. Matrix: latest
  stable Python on `ubuntu-latest` + `windows-latest` (the colleague is on Windows).
  Steps: `uv sync --all-extras --dev`, `uv run ruff check .`, `uv run ruff format --check .`,
  `uv run mypy src/`, `uv run pytest --cov`, upload coverage.
- **`.github/workflows/release.yml`** — triggered on git tags `v*.*.*`. Builds
  sdist + wheel with `uv build`, publishes to PyPI via trusted publishing
  (no API tokens needed once configured), creates a GitHub Release with auto-generated
  changelog from Conventional Commits.
- **`.github/workflows/integration.yml`** — runs nightly on `main`. Hits the sandbox
  Recombee database. Posts a summary comment if anything regressed.

Dependabot (or Renovate) config for weekly dependency PRs.

---

## 4. Architecture

### 4.1 MCP server design

The server exposes **tools** (callable functions) only — no resources or prompts
in M1. Tools are grouped into modules under `src/recombee_mcp/tools/`:

```
tools/
├── __init__.py        # Tool registration helper
├── recommendations.py # RecommendItemsToUser, RecommendItemsToItem, etc.
├── catalog.py         # GetItemValues, ListItems, ListItemProperties
├── scenarios.py       # Scenario inspection (read-only)
├── search.py          # SearchItems (personalized full-text)
└── segments.py        # Segmentations, Item Segments inspection
```

Each module exports decorated functions that are registered with the central
`FastMCP` instance in `server.py`. One function = one tool. Every function:

- Has a complete docstring (used as the tool description for the LLM).
- Has fully-typed parameters and return value.
- Catches Recombee `ApiException` and re-raises as a clear `ToolError`.
- Returns a JSON-serializable dict (Pydantic models auto-serialize via FastMCP).

### 4.2 Security model

This is the most critical section. The Recombee private API token can wipe
the entire database. Treat it like a production database password.

**Hard rules (non-negotiable):**

1. **No `ResetDatabase`, `DeleteItem`, `DeleteUser`, `DeleteItemProperty`,
   `DeleteUserProperty`, `DeleteScenario`, or any `Delete*` operation is exposed
   as a tool.** Ever. If the human asks for one, refuse and explain why.
2. **Read-only by default.** All write operations live behind a single boolean
   `RECOMBEE_WRITE_ENABLED` env var (default `false`). When `false`, write tools
   are not registered with FastMCP at all — the LLM cannot see them.
3. **Sandbox database for experiments.** Configuration supports two modes via
   `RECOMBEE_PROFILE` env var: `production` (read-only, no write tools registered
   regardless of `RECOMBEE_WRITE_ENABLED`) and `sandbox` (both read and write
   tools available if `RECOMBEE_WRITE_ENABLED=true`). The profile is logged at
   startup and included in every tool's metadata returned to the LLM.
4. **ReQL filter validation.** Any tool that accepts a user-supplied ReQL filter
   string runs it through a basic allowlist parser (we don't need full grammar —
   just reject filters containing function names not in our known set, and reject
   property names not present in `ListItemProperties`). Bad input → clear error,
   no SDK call.
5. **Audit log.** Every tool call writes a JSONL line to
   `~/.local/share/recombee-mcp/audit.log` (XDG-compliant; on Windows use
   `%LOCALAPPDATA%/recombee-mcp/audit.log`) with timestamp, profile, tool name,
   parameters (truncated), and outcome. Use `platformdirs` for cross-platform paths.
6. **Confirmation pattern for write tools.** Every write tool takes a required
   `confirm: bool` parameter. If `confirm=False` (the default), the tool returns
   a dry-run summary without calling the Recombee API. The LLM must explicitly
   re-call with `confirm=True` to perform the write.

**Soft rules (defaults; document deviations in `.claude-plans/`):**

- Bulk operations (`Batch` requests) are capped at 100 items per call to limit
  blast radius. Configurable via env var.
- All tools include `database_id` in their response metadata so the LLM cannot
  silently switch contexts.

### 4.3 Configuration

Use **`pydantic-settings`** to load from env + optional `.env`:

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="RECOMBEE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid",
    )
    db_id: str
    private_token: SecretStr
    region: Literal["eu-west", "us-west", "ap-se", "ca-east"] = "eu-west"
    profile: Literal["production", "sandbox"] = "production"
    write_enabled: bool = False
    integration_db_id: str | None = None       # for integration tests
    integration_token: SecretStr | None = None
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    audit_log_dir: Path | None = None          # default: platformdirs
    batch_max_size: PositiveInt = 100
```

Settings are instantiated once in `server.py` and passed (or imported) wherever
needed. Tests use `Settings(db_id="test", private_token="x", ...)` directly.

---

## 5. Initial tool surface (Milestone M1)

Ship M1 as **read-only only**. Write tools land in M2 after security review.

### M1 — read-only tools

| Tool name              | Wraps SDK request                  | Purpose                                                      |
|------------------------|------------------------------------|--------------------------------------------------------------|
| `recommend_to_user`    | `RecommendItemsToUser`             | Personalized recs for a user, scenario optional              |
| `recommend_to_item`    | `RecommendItemsToItem`             | Related-items / "because you viewed" recs                    |
| `recommend_next_items` | `RecommendNextItems`               | Pagination follow-up to a previous recommendation            |
| `search_items`         | `SearchItems`                      | Personalized full-text search                                |
| `get_item_properties`  | `GetItemValues`                    | All property values for one item                             |
| `list_items`           | `ListItems`                        | Item IDs (paginated; `filter` and `count` optional)          |
| `list_item_properties` | `ListItemProperties`               | Schema of items in this database                             |
| `list_user_properties` | `ListUserProperties`               | Schema of users in this database                             |
| `get_user_properties`  | `GetUserValues`                    | All property values for one user                             |
| `list_segmentations`   | `ListSegmentations`                | Configured segmentations                                     |
| `recommend_segments_to_user` | `RecommendItemSegmentsToUser`| Top categories/brands for a user                             |

Plus one diagnostic meta-tool:

- **`describe_setup`** — returns the configured profile, region, db_id (not token!),
  enabled tools, and a summary of properties/scenarios present. Used by Claude
  to orient itself at the start of a debugging session.

### M2 — write tools (later, separate plan in `.claude-plans/`)

Item property creation, item value updates, scenario filter modifications, etc.
Each requires `confirm=True`, runs only in `sandbox` profile, and gets its own
review.

### Out of scope, possibly forever

- `ResetDatabase` and any `Delete*` — see §4.2.
- Direct interaction-sending tools (`AddPurchase`, `AddDetailView`, etc.) —
  these belong in the e-shop application code, not in an AI debugging tool.
  If we ever expose them, it's only for synthetic test-data generation in a
  sandbox, with extreme rate-limiting.

---

## 6. Project structure

```
recombee-mcp/
├── .claude/                       # Claude Code project config (see §7)
│   ├── settings.json              # permissions, hooks (committed)
│   ├── settings.local.json        # personal overrides (gitignored)
│   ├── skills/                    # project-specific skills
│   │   ├── recombee-api/SKILL.md
│   │   ├── testing/SKILL.md
│   │   └── security/SKILL.md
│   ├── commands/                  # custom slash commands
│   │   ├── new-tool.md
│   │   └── plan.md
│   └── agents/                    # subagents
│       ├── code-reviewer.md
│       └── security-auditor.md
├── .claude-plans/                 # implementation plans (committed)
│   ├── README.md                  # explains the convention
│   ├── 01-initial-implementation.md
│   └── ...
├── .github/
│   ├── workflows/
│   │   ├── ci.yml
│   │   ├── release.yml
│   │   └── integration.yml
│   ├── dependabot.yml
│   └── ISSUE_TEMPLATE/
├── docs/
│   ├── index.md                   # mkdocs entry; optional in M1
│   ├── architecture.md
│   ├── security.md
│   └── tools.md                   # generated reference
├── src/
│   └── recombee_mcp/
│       ├── __init__.py            # __version__ defined here
│       ├── __main__.py            # `python -m recombee_mcp`
│       ├── server.py              # FastMCP instance & main()
│       ├── settings.py            # pydantic-settings
│       ├── client.py              # RecombeeClient factory
│       ├── audit.py               # JSONL audit logger
│       ├── errors.py              # custom exception hierarchy
│       ├── reql.py                # ReQL allowlist validator
│       └── tools/
│           ├── __init__.py
│           ├── recommendations.py
│           ├── catalog.py
│           ├── scenarios.py
│           ├── search.py
│           ├── segments.py
│           └── meta.py            # describe_setup
├── tests/
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_settings.py
│   │   ├── test_audit.py
│   │   ├── test_reql.py
│   │   └── tools/
│   │       ├── test_recommendations.py
│   │       └── ...
│   └── integration/
│       └── test_live_sandbox.py
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── .python-version                # uv reads this
├── CHANGELOG.md                   # keep-a-changelog format
├── CLAUDE.md                      # production version (replaces this brief)
├── CONTRIBUTING.md
├── LICENSE                        # MIT or Apache-2.0 — ask the human
├── README.md
├── SECURITY.md                    # vuln disclosure policy
├── pyproject.toml
└── uv.lock
```

---

## 7. Claude Code project setup

This project itself uses Claude Code. Configure it as a first-class citizen.

### 7.1 Production `CLAUDE.md` (replaces this brief once M1 ships)

After M1 is implemented, **rewrite** this `CLAUDE.md` into a lean (<150 lines)
production version. Move long-form rationale into `docs/architecture.md` and
`docs/security.md`. The production `CLAUDE.md` should contain:

- One-paragraph project overview
- Stack at a glance (Python version, key libs, test commands)
- The non-negotiable security rules from §4.2 (verbatim)
- The "plans live in `.claude-plans/`" rule
- Pointers (`@docs/architecture.md`, `@docs/security.md`, `@.claude/skills/`)
- Common commands (test, lint, type-check, run-server, run-inspector)

Keep it under 200 lines. Long files cost tokens on every session start.

### 7.2 `.claude/settings.json`

Committed. Contains:

- `permissions.allow`: `["Bash(uv run *)", "Bash(uv add *)", "Bash(uv sync *)",
  "Bash(uv build *)", "Bash(git status)", "Bash(git diff *)", "Bash(git log *)",
  "Bash(pytest *)", "Bash(ruff *)", "Bash(mypy *)", "Read(**)", "Write(**)",
  "Edit(**)"]`
- `permissions.deny`: `["Read(./.env)", "Read(./.env.local)", "Bash(rm -rf *)",
  "Bash(git push --force*)", "Bash(curl * | sh)", "Bash(uv run python -c *ResetDatabase*)"]`
- `hooks.PreToolUse` for `Edit|Write` matching `**/*.py` runs `uv run ruff format -`
  on the new content as a sanity-check (nice-to-have; skip if it slows things down).
- `hooks.PostToolUse` for `Edit|Write` matching `pyproject.toml` runs `uv lock`
  to keep the lockfile current.
- Attribution: `attribution.commit: ""` so commits don't get an auto co-author line.

### 7.3 `.claude/settings.local.json` (gitignored, personal)

Used by individual contributors for personal model preferences, extra MCP servers
they have locally, etc. The repo provides a documented example in `CONTRIBUTING.md`.

### 7.4 `.mcp.json` — MCP servers used **by this project's Claude Code**

Committed. Configures Claude Code to use:

```json
{
  "mcpServers": {
    "context7": {
      "type": "http",
      "url": "https://mcp.context7.com/mcp",
      "headers": { "CONTEXT7_API_KEY": "${CONTEXT7_API_KEY}" }
    }
  }
}
```

Document in `CONTRIBUTING.md` that contributors set `CONTEXT7_API_KEY` in their
shell. Free key from https://context7.com/dashboard; paid tier is fine if needed.

**Why Context7:** the FastMCP and Recombee SDKs evolve. When Claude Code writes
new tools or refactors plumbing, it should fetch current docs rather than guess
from training data. Add to production `CLAUDE.md`: *"For any FastMCP, Recombee
SDK, pydantic, ruff, mypy, or pytest API question — query Context7 first."*

### 7.5 Skills to install

Be selective. Each skill consumes baseline context. Stick to ones with clear ROI:

**Project-local skills (always loaded — `.claude/skills/`):**

1. **`recombee-api/SKILL.md`** — Recombee SDK conventions, common request
   patterns, error handling idioms specific to this project.
2. **`testing/SKILL.md`** — how we mock the SDK, fixtures, test naming, when to
   write integration tests.
3. **`security/SKILL.md`** — the §4.2 rules restated as a skill, with examples
   of what to refuse.

**User-level skills to consider (run `claude skills add ...`):**

- `anthropics/claude-code-plugins` — baseline quality, official.

Don't add general "TDD skills" or "code-reviewer skills" unless they earn it
in practice. The community consensus (mid-2026) is that 2–3 skills max produces
better outputs than 20 — context noise hurts more than skill content helps.

### 7.6 Custom slash commands (`.claude/commands/`)

- **`/new-tool <name>`** — scaffold a new MCP tool: stub function in the right
  module, draft test file, update `tools/__init__.py` registration, suggest
  tool description. The user fills in the body.
- **`/plan <slug>`** — create a new `.claude-plans/NN-<slug>.md` from a template.
  Auto-numbers based on existing files.
- **`/inspector`** — run `uv run fastmcp dev src/recombee_mcp/server.py` so the
  human can poke at tools through the MCP Inspector UI.

### 7.7 Subagents (`.claude/agents/`)

- **`code-reviewer.md`** — invoked after a feature is implemented. Reviews diff
  against `.claude/skills/security/SKILL.md` rules and the conventions in this
  brief.
- **`security-auditor.md`** — runs before merging M2 (write tools). Audits every
  new write tool against §4.2.

### 7.8 Hooks (`.claude/settings.json`)

Beyond the formatting hooks above, add:

- **`UserPromptSubmit` hook** (optional, polite): if the prompt includes the words
  "delete", "drop", "reset", or "wipe" alongside "database" or "Recombee", show
  a soft warning ("This project disallows destructive Recombee operations — see
  CLAUDE.md §4.2"). Doesn't block, just nudges.

---

## 8. Workflow conventions

### 8.1 Plans live in `.claude-plans/`

Before non-trivial work:

1. Create `.claude-plans/NN-<slug>.md` (zero-padded number, kebab-case slug).
2. Sections: **Goal**, **Context**, **Approach**, **File-level changes**,
   **Test plan**, **Risks**, **Rollback**, **Status** (Draft / Approved /
   In progress / Done / Abandoned).
3. Wait for human approval (status flips to Approved) before executing.
4. As you implement, update **Status** and append a **Notes** section with
   anything unexpected.
5. Plans are committed to git as part of the same PR as the implementation.
6. Plans are append-only history. Don't delete old ones — they document the
   reasoning trail.

`.claude-plans/README.md` (you write this in your first action) explains the
convention to future contributors.

### 8.2 Conventional Commits

`type(scope): subject` — type ∈ `{feat, fix, docs, style, refactor, perf, test,
build, ci, chore, security}`. Scope is the affected module (`tools`, `audit`,
`reql`, etc.) or `repo` for cross-cutting. Subject ≤ 72 chars, imperative mood,
no trailing period.

Example: `feat(tools): add recommend_segments_to_user tool`

The pre-commit hook validates this. Auto-changelog generation in the release
workflow depends on it.

### 8.3 Branch strategy

- `main` is always green and deployable.
- Feature branches: `feat/<slug>`, `fix/<slug>`, `docs/<slug>`.
- Squash-merge to `main` via PR. PR title follows Conventional Commits — that
  becomes the squash commit message.

### 8.4 PR checklist (template at `.github/pull_request_template.md`)

- [ ] Plan in `.claude-plans/` linked
- [ ] Tests added/updated; coverage didn't drop below threshold
- [ ] `ruff check .` clean
- [ ] `mypy src/` clean
- [ ] CHANGELOG.md updated under `## [Unreleased]`
- [ ] If new public API: `docs/tools.md` regenerated
- [ ] If new env var: `.env.example` updated, `README.md` config table updated
- [ ] Security checklist (for any write tool): see `.claude/skills/security/SKILL.md`

### 8.5 Versioning & releases

Semantic Versioning. `__version__` lives in `src/recombee_mcp/__init__.py` as
the single source of truth. Bumping it + creating a `vX.Y.Z` git tag triggers
the release workflow. Until 1.0.0, anything may break between minors.

---

## 9. Open-source readiness

When the project is opened to the world (could be from day one or after M1):

- **README.md** — badges (CI status, PyPI version, Python versions, license),
  one-paragraph pitch, "what is Recombee" link, install instructions
  (`uv tool install recombee-mcp` and Claude Desktop config snippet),
  feature list with the tool table from §5, security model summary linking to
  `docs/security.md`, contributing pointer, license.
- **LICENSE** — ask the human: MIT (maximal permissiveness) or Apache-2.0 (adds
  patent grant). MIT is the default if no preference.
- **CONTRIBUTING.md** — how to set up locally, run tests, the `.claude-plans/`
  convention, Conventional Commits, code-of-conduct pointer.
- **CODE_OF_CONDUCT.md** — Contributor Covenant 2.1.
- **SECURITY.md** — how to report vulnerabilities (private GitHub Security
  Advisory or email), supported versions table.
- **CHANGELOG.md** — keep-a-changelog format. `## [Unreleased]` section at top.
  Release workflow promotes Unreleased to a versioned section on tag.
- **`.github/ISSUE_TEMPLATE/`** — bug report, feature request templates.
- **`.github/FUNDING.yml`** — optional, ask the human.
- **PyPI metadata in `pyproject.toml`** — keywords (`mcp`, `recombee`,
  `recommendation`, `claude`, `ai-tools`), classifiers, project URLs (Homepage,
  Documentation, Issues, Changelog).

A first-time visitor should be able to: `uv tool install recombee-mcp`, copy
the Claude Desktop snippet from the README, set 2 env vars, and have working
tools in under 5 minutes.

---

## 10. The user (so future-you knows the context)

- **Role:** PHP developer working as e-commerce consultant for a Czech/Slovak
  premium kitchenware e-shop (Potten & Pannen).
- **Comfort level:** strong with PHP, comfortable with Python (no aversion),
  values modern best-practice tooling.
- **Operating system:** developing on his own machine (preferences captured by
  Claude Code locally); the server will also run on a Windows 11 colleague's
  machine. **No Docker on the colleague's box** — the install path is `winget
  install astral-sh.uv` then `git clone` then a Claude Desktop config snippet.
  Cross-platform path handling matters (use `pathlib`, `platformdirs`).
- **Budget:** open for paid tooling that earns its keep (Context7 paid tier OK).
- **Endgame:** open-source release on GitHub, possibly a blog post about the
  setup. Quality bar reflects that.

---

## 11. Your first actions, Claude Code

Do these in order. Don't skip steps. Don't start coding before §11.4.

### 11.1 Confirm environment

Before anything else, verify:

- `uv --version` works. If not, instruct the human to install it
  (`winget install astral-sh.uv` on Windows, `curl -LsSf https://astral.sh/uv/install.sh | sh`
  on Unix) and stop until they confirm.
- `python --version` against the latest stable (check
  https://www.python.org/downloads/). If older, run `uv python install <latest>`.
- `git --version` works.
- The folder is genuinely empty except for this file. If not, ask before touching
  anything.

### 11.2 Ask the human the few things you can't infer

Use the AskUserQuestion-style approach — group questions, don't drip-feed.
Specifically:

1. **License:** MIT or Apache-2.0?
2. **GitHub repo name:** default `recombee-mcp`; confirm or override.
3. **Author name + email** for `pyproject.toml` and `LICENSE`.
4. **PyPI publish from day one?** (Sets up trusted publishing now vs. later.)
5. **Context7 API key** — do they want to set it up now or later? (Server can
   run without it.)
6. **Recombee credentials** — do they have a sandbox database ID + private token
   ready to drop into `.env`, or should we use placeholders for now?

If the human says "use your judgment", pick MIT, `recombee-mcp`, ask for the
name/email, defer PyPI to v0.1.0, defer Context7, and use placeholders.

### 11.3 Write the initial plan

Create `.claude-plans/01-initial-implementation.md`. Use the structure from §8.1.
Break M1 into ordered phases, e.g.:

1. Repo skeleton (pyproject, uv setup, basic structure, README/LICENSE/CHANGELOG stubs)
2. Settings + audit + errors (foundation modules with tests)
3. Client factory + first tool (`describe_setup`) + smoke test
4. Read-only tools, one module at a time, each with tests
5. Pre-commit + CI workflow
6. `.claude/` directory contents (settings, skills, commands, agents)
7. Polish docs, README, prepare for first tag

Each phase has its own commit (or a small group of commits). Status starts as
**Draft**. Wait for the human to flip it to **Approved** before proceeding to §11.4.

Also write `.claude-plans/README.md` explaining the convention — short.

### 11.4 Execute, phase by phase

After approval, work through phases in order. After each phase:

- Run the full local check: `uv run ruff check . && uv run ruff format --check . && uv run mypy src/ && uv run pytest`.
- If green, commit with a Conventional Commit message.
- Update the plan's **Status** and **Notes** sections.
- Pause and report progress to the human before starting the next phase. Don't
  silently steamroll the whole thing.

### 11.5 Wrap-up

Once all phases of M1 are done:

- Replace **this** `CLAUDE.md` with the lean production version (§7.1).
- Create `.claude-plans/02-write-tools-plan.md` as a **Draft** placeholder for
  the M2 conversation, but don't implement it.
- Tag `v0.1.0` only after the human gives the green light — releases are not
  automatic.

Welcome aboard. Build it like it'll be on the front page of Hacker News next month.
