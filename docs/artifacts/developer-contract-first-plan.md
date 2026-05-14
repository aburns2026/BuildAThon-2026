# Developer Step Output: Contract-First MVP Plan

Date: 2026-05-14
Scope Constraint: docs/artifacts/scope-lock.md
Stack: FastAPI + React + Playwright TypeScript

## 1. Proposed Entities (Minimum)

### Employee
- id: string
- display_name: string
- status: active | inactive

### Punch
- id: string
- employee_id: string
- punch_type: IN | OUT
- occurred_at: datetime
- source: web | api
- validation_status: accepted | rejected
- validation_message: string | null

### Shift
- id: string
- employee_id: string
- start_at: datetime
- end_at: datetime | null
- duration_minutes: integer | null
- state: OPEN | CLOSED

### AuditEvent
- id: string
- employee_id: string
- event_type: CLOCK_IN_ACCEPTED | CLOCK_IN_REJECTED | CLOCK_OUT_ACCEPTED | CLOCK_OUT_REJECTED
- event_at: datetime
- source: web | api
- details: string

## 2. Proposed Endpoints (FastAPI Contract)

### POST /employees/{employeeId}/clock-in
Request body:
- source: optional string (default web)

Success response (200):
- shift_id
- employee_id
- status: CLOCKED_IN
- clock_in_at

Validation errors:
- 404 employee not found
- 409 duplicate open shift exists

### POST /employees/{employeeId}/clock-out
Request body:
- source: optional string (default web)

Success response (200):
- shift_id
- employee_id
- status: CLOCKED_OUT
- clock_out_at
- duration_minutes

Validation errors:
- 404 employee not found
- 409 no open shift exists

### GET /employees/{employeeId}/shifts
Query:
- limit: optional integer (default 10)

Success response (200):
- shifts: [{ shift_id, start_at, end_at, duration_minutes, state }]

### GET /employees/{employeeId}/audit-events
Query:
- limit: optional integer (default 20)

Success response (200):
- events: [{ event_id, event_type, event_at, source, details }]

### GET /employees/{employeeId}/payroll-summary
Query:
- period_start: optional date
- period_end: optional date

Success response (200):
- employee_id
- total_minutes_worked
- closed_shift_count
- period_start
- period_end

### GET /health
Success response (200):
- status: ok
- timestamp

## 3. Proposed UI Surface (React Minimum)

### MVP Screen A: Time Capture
- employee selector (or fixed demo employee)
- clock-in button
- clock-out button
- status badge: CLOCKED_IN or CLOCKED_OUT
- latest validation/error message

### MVP Screen B: Shift Summary
- list of recent shifts (start/end/duration/state)
- payroll summary card (total minutes, closed shifts)

### MVP Screen C: Audit Feed
- latest audit events list with event type and timestamp

## 4. Build Order (Next Implementation Slice)

1. Define Pydantic request/response models for all endpoints.
2. Implement in-memory repository layer for Employee, Punch, Shift, AuditEvent.
3. Implement clock-in service logic with duplicate open-shift rejection.
4. Implement clock-out service logic with no-open-shift rejection and duration calculation.
5. Implement shift list and payroll summary read endpoints.
6. Implement audit event writes for accepted and rejected punch actions.
7. Add React time-capture view and wire to clock-in/clock-out endpoints.
8. Add React summary and audit sections.
9. Add minimal API tests (clock-in success, duplicate reject, clock-out success).
10. Add one Playwright main-path test (clock-in to clock-out).

## 5. Risks Or Blockers

- Authentication is deferred; demo uses lightweight employee selection.
- Timezone handling can cause inconsistent duration if datetime handling is not normalized.
- If frontend starts before API schemas stabilize, integration churn will slow delivery.
- Push/auth environment in Codespaces can override credentials; use user-scoped auth when publishing.

## 6. Smallest Concrete Next Action

Implement and commit the backend contract skeleton first:
- add schema models
- add endpoint stubs for clock-in, clock-out, shifts, audit-events, payroll-summary
- return deterministic mock data and validation errors

This keeps API-first discipline and unblocks thin UI integration without widening scope.
