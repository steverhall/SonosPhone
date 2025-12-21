---

description: "Task list for feature: Generate tasks.md from design docs"

---

# Tasks: Generate tasks.md for 001-generate-tasks

**Input**: Design documents from `/specs/001-generate-tasks/`
**Prerequisites**: `plan.md`, `spec.md` in the feature directory

**Tests**: Unit tests for the tasks generator and format validator are included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure needed to build the generator

- [ ] T001 Create feature directory and placeholder design docs in specs/001-generate-tasks/ (specs/001-generate-tasks/plan.md, specs/001-generate-tasks/spec.md)
- [ ] T002 Initialize developer tooling (add pyproject.toml if missing) at /pyproject.toml
- [ ] T003 [P] Add `tools/` directory for small helper scripts at tools/
- [ ] T004 [P] Add a Makefile target `make tasks` that runs the generator: Makefile

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core utilities and validators that MUST be in place before user stories

- [ ] T005 Implement a prerequisites runner wrapper that invokes `.specify/scripts/bash/check-prerequisites.sh --json` and returns parsed JSON in `tools/prereq.py`
- [ ] T006 [P] Implement a lightweight markdown templating helper `tools/mdtemplate.py` to render `.specify/templates/tasks-template.md` with injected values
- [ ] T007 Implement a tasks format validator `tools/validate_tasks_format.py` that enforces the checklist format and file path rules
- [ ] T008 [P] Add unit test harness for the generator in `tests/test_tasks_generator.py`
- [ ] T009 Create CI check that runs `tools/validate_tasks_format.py` against generated tasks.md (add to .github/workflows/ci.yml)

---

## Phase 3: User Story 1 - Generate tasks.md (Priority: P1) 🎯 MVP

**Goal**: Produce `specs/001-generate-tasks/tasks.md` by reading `plan.md` and `spec.md` and filling `.specify/templates/tasks-template.md` with concrete tasks.

**Independent Test**: Run `python tools/generate_tasks.py --feature specs/001-generate-tasks` and verify `specs/001-generate-tasks/tasks.md` exists and passes `tools/validate_tasks_format.py`.

### Tests for User Story 1

- [ ] T010 [P] [US1] Add unit tests that exercise the generator input parsing in `tests/test_tasks_generator.py::test_parse_plan_and_spec`
- [ ] T011 [P] [US1] Add an end-to-end test `tests/test_tasks_generator.py::test_generate_tasks_md` that runs the generator and asserts checklist format

### Implementation for User Story 1

- [ ] T012 [US1] Implement the main generator `tools/generate_tasks.py` which:
  - reads `specs/<feature>/plan.md` and `specs/<feature>/spec.md`
  - maps user stories (P1,P2,P3...) to story IDs [US1],[US2],[US3]
  - produces concrete checklist tasks following the template and writes `specs/<feature>/tasks.md`
- [ ] T013 [P] [US1] Add CLI flags to `tools/generate_tasks.py` for `--feature`, `--dry-run`, and `--open` (file path: tools/generate_tasks.py)
- [ ] T014 [US1] Add logging to the generator and ensure errors are user-friendly (file: tools/generate_tasks.py)
- [ ] T015 [US1] Add integration test fixture files under `specs/001-generate-tasks/` used by tests (already present)

**Checkpoint**: Running generator should create `specs/001-generate-tasks/tasks.md` and tests should pass

---

## Phase 4: User Story 2 - Ensure tasks follow checklist format (Priority: P2)

**Goal**: Provide strict format validation and automated checks so generated tasks.md is immediately executable.

**Independent Test**: `tools/validate_tasks_format.py specs/001-generate-tasks/tasks.md` returns success (exit 0) and lists any violations otherwise.

### Tests for User Story 2

- [ ] T016 [P] [US2] Implement unit tests for the validator in `tests/test_tasks_validator.py::test_validator_accepts_good_tasks`
- [ ] T017 [P] [US2] Implement unit tests that assert validator rejects malformed checklist lines `tests/test_tasks_validator.py::test_validator_rejects_bad_tasks`

### Implementation for User Story 2

- [ ] T018 [US2] Implement `tools/validate_tasks_format.py` to enforce:
  - each task is a markdown checklist: `- [ ] T### [P]? [US?] Description path`
  - Task IDs are sequential (no duplicates)
  - Story labels `[US1]` appear for story tasks
  - File paths referenced exist or are plausible relative paths
- [ ] T019 [P] [US2] Add a `--fix` dry-run mode that suggests fixes but does not modify the file

**Checkpoint**: Validator unit tests pass and validator returns exit 0 on valid file

---

## Phase 5: User Story 3 - Validate templates (Priority: P3)

**Goal**: Ensure `.specify/templates/tasks-template.md` contains placeholders the generator can replace and update templates if needed.

**Independent Test**: Run generator with template and ensure placeholders are replaced and no bracket tokens remain.

### Tests for User Story 3

- [ ] T020 [P] [US3] Add tests to confirm template placeholder coverage `tests/test_template_coverage.py`

### Implementation for User Story 3

- [ ] T021 [US3] Review `.specify/templates/tasks-template.md` and update placeholders to align with generator requirements (file: .specify/templates/tasks-template.md)
- [ ] T022 [P] [US3] Propagate any required template updates to plan/spec/task templates in `.specify/templates/`
- [ ] T023 [US3] Add documentation describing the template placeholders in `specs/001-generate-tasks/quickstart.md`

**Checkpoint**: Template tests pass and generator renders tasks.md without leftover placeholders

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Add automation, docs, and CI to make the generator production-ready

- [ ] T024 [P] Add a CI workflow step `.github/workflows/generate-tasks.yml` that runs the generator and validator for new features
- [ ] T025 Update README explaining how to run the generator and where to find generated tasks: README.md
- [ ] T026 [P] Add logging and debug levels to `tools/generate_tasks.py` and `tools/validate_tasks_format.py`
- [ ] T027 [P] Add a convenience script `scripts/run_generate_tasks.sh` that runs the generator with recommended flags
- [ ] T028 [P] Manual review: Open a PR with generated `specs/001-generate-tasks/tasks.md` and request reviews from maintainers

---

## Dependencies & Execution Order

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS user stories
- **User Stories (Phase 3+)**: Depend on Foundational phase completion
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Order
- **US1 (P1)**: Implement generator and produce `tasks.md` - MVP
- **US2 (P2)**: Implement strict validator and tests
- **US3 (P3)**: Update templates and documentation

### Parallel Opportunities
- Tasks marked [P] can run in parallel (different files, no dependencies)
- Example parallel work: T006 (templating helper), T008 (unit tests), and T007 (validator) can be developed by separate contributors simultaneously

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (tools/prereq.py and mdtemplate)
3. Complete Phase 3: US1 (generator) and tests
4. **STOP and VALIDATE**: Run validator and tests
5. Merge and demo

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Implement US1 → Test independently → Merge
3. Implement US2 → Add validator tests → Merge
4. Implement US3 → Propagate template updates → Merge

---

## Implementation Notes

- Each task line has an explicit file path where work will occur when applicable
- Tests are included where requested in the spec
- Keep tasks small and focused so an LLM or engineer can implement them independently
- When a task references a file that does not yet exist, create it under the specified path


