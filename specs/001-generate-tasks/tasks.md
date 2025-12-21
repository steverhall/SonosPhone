---
description: "Task list for feature: 001-generate-tasks"
---

# Tasks: 001-generate-tasks

**Input**: Design documents from /specs/001-generate-tasks/
**Prerequisites**: `plan.md`, `spec.md`

**Goal**: Generate a clean `tasks.md` derived from `spec.md` user stories, with no unreplaced template tokens, pinned dependency tasks for Raspberry Pi, and CI validation steps.

## [US1] P1 - Generate tasks.md from existing design docs

- [ ] T101 [US1] Implement generator CLI: `tools/generate_tasks.py` — read `spec.md`/`plan.md`, render `tasks.md` into the feature folder. Acceptance: running generator produces `specs/001-generate-tasks/tasks.md` with no template sample sections and no unreplaced tokens. (path: tools/generate_tasks.py)
  - Verification: `python3 -m tools.generate_tasks --feature specs/001-generate-tasks --dry-run` prints the generated content; `tools/validate_tasks_format.py specs/001-generate-tasks/tasks.md` exits 0.

## [US2] P2 - Ensure tasks follow checklist format

- [ ] T102 [US2] Implement validator enhancements: `tools/validate_tasks_format.py` — fail if unreplaced placeholder tokens remain and return non-zero exit code with a list of offending tokens and line numbers. (path: tools/validate_tasks_format.py)
  - Verification: `python3 tools/validate_tasks_format.py specs/001-generate-tasks/tasks.md` returns non-zero and prints token locations if placeholders exist.

## [US3] P3 - Validate templates

- [ ] T103 [US3] Update templates: `.specify/templates/tasks-template.md` — remove sample task checklist blocks from the template or make them conditional. Acceptance: template can be rendered without leaving sample tasks in final output. (path: .specify/templates/tasks-template.md)
  - Verification: `python3 -m tools.generate_tasks --feature specs/001-generate-tasks --dry-run` shows no sample phases.

## Foundational / Cross-Cutting

- [ ] T104 [P] Add dependency pinning task: create `tools/export_pinned_requirements.py` or add step in generator to export pinned `requirements.txt` for Raspberry Pi (from `pyproject.toml` or lockfile). Acceptance: running the export creates `requirements-pinned.txt` in repo root. (path: tools/export_pinned_requirements.py)
  - Verification: `python3 tools/export_pinned_requirements.py --output requirements-pinned.txt`

- [ ] T105 [P] CI: Add `pip-audit` check to CI workflow for generated features and global deps. Acceptance: CI job runs `pip-audit` and fails on known vulnerabilities. (path: .github/workflows/pip-audit.yml)

## Notes
- The generator must strip or not emit the sample/template guidance blocks from the final `tasks.md`. Tasks must include precise file paths and acceptance criteria per the constitution. Tests are required for pure-Python logic as per constitution — mark tests as non-optional for functional pieces.
