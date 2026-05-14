# MVP Lock Decision

Date: 2026-05-14
Status: Locked
Scope Boundary Source: .github/skills/buildathon-mvp-4-hour/SKILL.md

## Locked In-Scope Capabilities
- Employee clock-in
- Employee clock-out
- Punch validation
- Duplicate punch prevention
- Shift history or today summary
- Audit log entries for punch actions
- Payroll-ready summary or export endpoint
- Small test set for API and one UI flow

## Explicitly Deferred
- Leave workflows
- Shift scheduling and break enforcement
- Full payroll rules including overtime, holiday, night differential, PTO, and comp time
- Full compliance reporting and CrossCheck reporting
- Deep enterprise architecture expansion (multi-company depth, full RBAC, CIAM, event-driven integration)

## Guardrails
- If a task does not improve the MVP demo path, it is out of scope.
- Any request that expands scope must be written as deferred unless explicitly approved.
- Backend contract and validation come before UI expansion.

## Entry Criteria To Start Implementation
- MVP stories complete
- Acceptance criteria complete
- Validation rules complete
- Deferred scope explicit

## Exit Criteria For MVP Implementation
- Clock-in works
- Duplicate or invalid punch is rejected
- Clock-out works
- Shift history or summary is visible
- Audit trail is visible
- Payroll summary or export is visible
- Minimal tests are runnable and pass for the main path

## Smallest Next Decision
Proceed to the Developer prompt and produce the thinnest contract-first implementation plan for entities, endpoints, UI surface, and build order.
