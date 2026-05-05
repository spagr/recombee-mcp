# Implementation Plans

This directory contains implementation plans for non-trivial changes to the project.

## Convention

- Filename format: `NN-short-slug.md` (zero-padded number, kebab-case)
- Created **before** implementation begins
- Reviewed by a human before execution (status: Draft → Approved)
- Plans are append-only history — never delete old ones

## Template

```markdown
# NN — Title

## Goal

What we're trying to achieve and why.

## Context

Background info, constraints, prior decisions.

## Approach

Step-by-step plan with file-level changes.

## Test Plan

How we'll verify correctness.

## Risks

What could go wrong and how we mitigate it.

## Rollback

How to undo if things go wrong.

## Status

Draft | Approved | In progress | Done | Abandoned

## Notes

(Appended during implementation)
```
