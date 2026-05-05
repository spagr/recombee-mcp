# /plan

Create a new implementation plan in `.claude-plans/`.

## Usage

`/plan <slug>`

## What it does

1. Count existing plans in `.claude-plans/` to determine the next number
2. Create `.claude-plans/NN-<slug>.md` with the standard template
3. Set status to **Draft**

## Template

```markdown
# NN — Title

## Goal

[What we're trying to achieve and why]

## Context

[Background, constraints, prior decisions]

## Approach

[Step-by-step plan with file-level changes]

## Test Plan

[How we'll verify correctness]

## Risks

[What could go wrong]

## Rollback

[How to undo]

## Status

Draft

## Notes

(Appended during implementation)
```
