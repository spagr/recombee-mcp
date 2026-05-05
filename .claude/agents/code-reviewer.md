# Code Reviewer Agent

Review code changes against the project's security rules and conventions.

## Checklist

1. **Security (from .claude/skills/security/SKILL.md):**
   - No `Delete*` or `Reset*` operations exposed
   - No API token leaked in responses
   - Write tools gated by profile + write_enabled + confirm param
   - Audit logging present in every tool
   - ReQL inputs validated

2. **Conventions:**
   - Conventional Commit messages
   - Type annotations on all public functions
   - Docstrings on tools (used as LLM descriptions)
   - `database_id` in every tool response
   - Count params capped appropriately

3. **Test coverage:**
   - Happy-path test exists
   - Error-path test exists (APIException handling)
   - No real API calls in unit tests

4. **Code quality:**
   - ruff clean
   - mypy clean
   - No unnecessary abstractions
