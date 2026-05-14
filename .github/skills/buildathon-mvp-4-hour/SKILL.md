---
name: buildathon-mvp-4-hour
description: 'Execute the BBSI BuildAThon as a realistic 4-hour MVP. Use when the team or individual needs a narrow, demoable slice instead of attempting the full Workforce Time Tracking and Payroll Integration Platform.'
argument-hint: 'Optional focus such as solo mode, MVP first, or time capture slice'
user-invocable: true
---

# BuildAThon MVP 4-Hour Mode

Use this skill when the BuildAThon is time-boxed to roughly four hours and the full requirements set is not realistically buildable.

This skill is the execution overlay for the larger plan in `../buildathon-plan-of-attack/SKILL.md`.
Read the main plan for full context, then use this skill as the primary delivery target.

## Chosen Stack

Use these fixed technology choices for the MVP unless the starter repo makes them impossible:

- Backend API: FastAPI
- Frontend UI: React
- End-to-end UI tests: Playwright with TypeScript

## Purpose

Do not try to build the entire Workforce Time Tracking and Payroll Integration Platform in four hours.

The goal is to deliver one credible, end-to-end slice that proves:

- functional delivery
- API-first design
- AI-assisted development workflow
- basic automated testing
- basic security awareness
- basic operational readiness

This skill assumes a solo builder or a very small group working under severe time pressure.

## The 4-Hour MVP

The MVP is a time-capture slice with payroll readiness, not a full workforce platform.

### In Scope

Build these capabilities first:

1. Employee clock-in
2. Employee clock-out
3. Punch validation
4. Duplicate punch prevention
5. Basic attendance or shift history view
6. Audit log for punch actions
7. Payroll-ready export or summary endpoint for worked time
8. One API contract surface that supports web and future mobile clients
9. Minimal responsive UI behavior for the time-capture flow
10. A very small automated test set

### Explicitly Out Of Scope

Do not attempt these unless the MVP is stable and time remains:

- Leave request workflows
- Leave approval workflows
- Shift scheduling
- Break enforcement
- Core-hour validation
- Attendance exception management beyond simple invalid punches
- Overtime rules beyond a placeholder or clearly deferred design note
- Holiday rules
- Night differential
- PTO and comp time management
- Full compliance reporting
- CrossCheck reporting
- Multi-company depth
- Multi-location depth
- Full RBAC system
- Real CIAM integration
- Event-driven architecture
- Full support and BugBot implementation inside the product

## MVP Narrative

The demo should tell a simple, believable story:

1. An employee clocks in.
2. The system rejects an invalid or duplicate punch.
3. The employee clocks out.
4. The system shows worked time in a timesheet or shift history view.
5. The system records an audit trail.
6. The system exposes a payroll-ready export or summary.
7. Automated tests prove the main flow and one failure path.

If you can demonstrate that clearly, you have a credible BuildAThon submission even if the rest of the platform is deferred.

## Minimum Deliverables

To consider the MVP complete, deliver at least these artifacts:

- Working UI for clock-in and clock-out
- Working FastAPI backend for time capture and history
- Basic persistence for employee, punch, shift, and audit data
- API documentation or a concise contract summary
- At least 2 API tests
- At least 1 Playwright TypeScript UI flow test
- A short architecture note
- A short deferred-scope note

## Core Domain Model

Keep the model small. Start with only what the MVP needs.

### Suggested Entities

- Employee
  Minimal identity fields, status, and a company or location placeholder field if needed
- Punch
  Employee ID, punch type, timestamp, source, validation status
- Shift
  Employee ID, start time, end time, duration, status
- AuditEvent
  Event type, target record, timestamp, actor, details

You can add a PayrollExport view or DTO without building a full payroll engine.

## Minimum API Surface

Keep the API narrow and explicit.

Implement the API in FastAPI.

### Suggested Endpoints

- `POST /employees/{employeeId}/clock-in`
- `POST /employees/{employeeId}/clock-out`
- `GET /employees/{employeeId}/shifts`
- `GET /employees/{employeeId}/audit-events`
- `GET /employees/{employeeId}/payroll-summary`

Optional:

- `GET /health`

### Required Behaviors

- Reject duplicate open clock-ins
- Reject clock-out when no open shift exists
- Persist audit events for successful and rejected actions when feasible
- Return validation errors clearly
- Keep request and response shapes simple and demoable

## Minimum UI Surface

Do not build an admin suite.

Implement the UI in React.

Build only:

- Employee selection or a simple fixed demo employee flow
- Clock-in action
- Clock-out action
- Current status indicator
- Shift history or today summary
- Validation and error messages
- Lightweight responsive layout that works on a small screen width

## Minimum Test Strategy

Testing is part of the MVP, but keep it narrow.

### Required API Tests

- Successful clock-in
- Duplicate clock-in rejected
- Successful clock-out after open shift exists

### Required UI Test

- One Playwright TypeScript test where the user clocks in, clocks out, and sees updated status or history

### Nice To Have If Time Remains

- Clock-out without open shift rejected
- Payroll summary endpoint returns worked duration

## Minimum Security Posture

Do not overbuild security, but do not ignore it.

At minimum:

- Avoid hardcoded secrets
- Validate request inputs
- Return safe error messages
- Keep any demo auth story honest and lightweight
- If real authentication is not implemented, state that clearly as deferred

## Minimum Platform Posture

For a 4-hour sprint, platform maturity means the project can be started and demoed predictably.

At minimum:

- Clear startup steps
- Reproducible local or Codespaces run path
- One command or short sequence to run the app
- One command or short sequence to run tests
- Basic logs visible during runtime

## Time Budget

Use the four hours aggressively.

### Hour 1

- Read the requirements and plan skill
- Lock the MVP scope
- Define entities and API contracts
- Scaffold the FastAPI backend, React frontend, and core data model

### Hour 2

- Implement clock-in and clock-out backend flows
- Add validation and audit logging
- Persist core entities

### Hour 3

- Build the thin UI flow
- Connect UI to the API
- Add shift history or summary view

### Hour 4

- Add automated tests
- Add Playwright TypeScript coverage for the main UI flow and a small API test set
- Clean up errors and demo flow
- Write the short architecture and deferred-scope notes
- Verify startup and run instructions

## Decision Rules

- Prefer one polished vertical slice over multiple incomplete features.
- Prefer honest deferral over fake completeness.
- Prefer simple persistence over speculative enterprise design.
- Prefer contract clarity over framework cleverness.
- Prefer demo stability over feature count.
- If a feature does not help the demo, cut it.

## Done Criteria

The MVP is done when:

- The user can clock in and clock out successfully
- Invalid punch behavior is demonstrated
- Worked time is visible in history or summary
- Audit events exist for the core flow
- A payroll-ready summary or export is available
- The main flow is covered by a small automated test set
- The app can be started and demonstrated reliably
- Deferred areas are explicitly documented instead of silently omitted

## How To Use This Skill

1. Read the main plan skill and the requirements document.
2. Adopt this MVP as the primary execution target.
3. Avoid expanding scope unless the current MVP is complete.
4. Use role-specific prompts only when they help move the MVP forward.
5. Keep the demo story in mind while making every implementation decision.

## Recommended Order Of Operations

1. PO or BA prompt for MVP stories and acceptance criteria
2. Developer prompt for contracts, schema, backend, and UI slice
3. QA prompt for minimal high-value tests
4. Security prompt for a lightweight final review
5. Support or BugBot prompts only if there is extra time or explicit judging pressure

## Final Reminder

This BuildAThon brief is broader than the time box supports.

Your job is not to honor every bullet equally.
Your job is to produce a stable, credible MVP that clearly maps to the requirements and can be explained as the first slice of a larger platform.