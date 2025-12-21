<!--
Sync Impact Report
Version change: none → 1.0.0
Modified principles: Added 5 principles (Simplicity & Hardware-First; Reproducible Environments; Test & Validate; Documentation & On-Device UX; Safety, Security & Observability)
Added sections: Development Workflow, Additional Constraints
Removed sections: none
Templates requiring updates: 
  - .specify/templates/plan-template.md ⚠ pending
  - .specify/templates/spec-template.md ⚠ pending
  - .specify/templates/tasks-template.md ⚠ pending
  - .specify/templates/checklist-template.md ⚠ pending
  - .specify/templates/agent-file-template.md ⚠ pending
Follow-up TODOs: none
-->

# SonosPhone Constitution

## Core Principles

### Simplicity & Hardware-First
Every change MUST keep the device’s primary function (hardware control and UX) simple, reliable,
and maintainable. Non-negotiable rules:
- MUST prioritize minimal dependencies on the device (Raspberry Pi Zero/Zero W class hardware).
- MUST prefer synchronous, easy-to-debug I/O (text/stdout or structured logs) for device interactions.
- MUST avoid feature creep that materially increases hardware resource requirements.

### Reproducible Environments & Dependency Control
Development and deployment environments MUST be reproducible and explicitly declared.
Non-negotiable rules:
- MUST document runtime dependencies (Python version, Node service versions) in requirements.txt
  and short machine-readable form where applicable.
- MUST pin external service versions when used in CI or on-device (e.g., node-sonos-http-api).
- SHOULD provide simple local reproduction steps for new contributors.

### Test & Validate (NON-NEGOTIABLE where feasible)
Testing is REQUIRED where it can prevent regressions; for hardware-bound flows prefer integration
tests and manual validation steps. Non-negotiable rules:
- MUST include unit tests for pure-Python logic and integration tests or step-by-step validation
  instructions for hardware interactions.
- MUST include a failing test that demonstrates the expected behavior before implementing a fix
  (TDD encouraged where practical).

### Documentation & On-Device UX
Documentation is part of the deliverable. The project MUST remain usable by a hobbyist
or future maintainer without tribal knowledge. Non-negotiable rules:
- MUST document setup, wiring diagrams, and quickstart steps in README.md or docs/quickstart.md.
- MUST include user-facing command mappings (keypad table) and any calibration or alignment steps.

### Safety, Security & Observability
Safety and privacy MUST be considered for all changes. The project MUST expose observability
signals that make debugging on-device possible. Non-negotiable rules:
- MUST avoid storing sensitive credentials in plaintext in the repo.
- MUST provide structured logs or clear stdout/stderr messages for runtime issues.
- MUST document any network services and their expected access controls.

## Additional Constraints

Technology & deployment constraints for SonosPhone:
- Primary hardware: Raspberry Pi (Zero/3/4 families) — aim for minimal CPU/memory usage.
- Primary language: Python 3.9+ for device code; Node.js for node-sonos-http-api (if used).
- Services are managed as systemd units on the device (see ReadKey/*.service files).
- Camera-based album scanning is optional; include calibration and privacy notes when enabled.

## Development Workflow

Code changes, documentation, and governance:
- Work in feature branches; open a pull request that references the related spec/plan when
  the change is non-trivial.
- All PRs MUST include: description, testing steps, any required hardware setup, and
  updated documentation if user-visible behavior changes.
- A maintainer (repo owner or a designated reviewer) MUST approve changes before merge.

## Governance

Amendments and versioning policy:
- Amendments: Changes to this constitution are made via a documented PR. The PR MUST
  include a rationale, migration steps for breaking changes, and an explicit version bump.
- Approval: Amendments MUST be approved by at least one repository maintainer (owner).
- Review period: Normal amendments SHOULD have a minimum 7-day review window. Emergency
  fixes (security or safety) MAY be fast-tracked with post-hoc ratification.

Versioning policy (semantic):
- MAJOR: Backwards-incompatible governance or principle removals.
- MINOR: Addition of a new principle or materially expanded guidance.
- PATCH: Wording, clarifications, or typo fixes.

Compliance expectations:
- PRs that change behavior that the constitution constrains MUST include a short compliance
  checklist verifying each affected principle.

**Version**: 1.0.0 | **Ratified**: 2025-12-21 | **Last Amended**: 2025-12-21
