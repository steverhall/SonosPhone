# Spec for 001-generate-tasks

P1: Generate tasks.md from existing design docs
- As a developer I want a tasks.md that maps user stories to implementation tasks so I can implement them independently.

P2: Ensure tasks follow checklist format
- As a maintainer I want all tasks formatted with Task IDs and file paths so they are executable by LLMs and engineers.

P3: Validate templates
- As a release manager I want templates updated to match generated content.

## Acceptance Criteria

- US1: Running the generator on this feature produces `specs/001-generate-tasks/tasks.md` with no unreplaced tokens and at least one task per user story.
	- Verification: `python3 -m tools.generate_tasks --feature specs/001-generate-tasks --dry-run` and then `python3 tools/validate_tasks_format.py specs/001-generate-tasks/tasks.md` returns exit code 0.
- US2: Validator fails when placeholder tokens exist.
	- Verification: Insert a placeholder into tasks.md and confirm validator returns non-zero.
- US3: Templates do not inject sample checklist content into generated `tasks.md`.
	- Verification: Generated `tasks.md` contains only header + story sections (no Phase 1..N sample blocks).
