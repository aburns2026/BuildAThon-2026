# QA/STE Step Output: Minimum MVP Test Plan

Date: 2026-05-14
Scope Constraint: artifacts/mvp-lock.md
Stack: FastAPI API + React UI + Playwright TypeScript

## 1. MVP Test Plan

Goal: prove the main MVP demo path with the fewest high-value tests.

Coverage target:
- one happy path from clock-in to clock-out
- one failure path for duplicate or invalid punch
- visibility check for summary/history output

Test approach:
- API-first verification for business rules
- one UI E2E test for demo confidence
- deterministic demo employee and repeatable timestamps where possible

## 2. Minimum API Tests

### API-1: Successful Clock-In
- Endpoint: POST /employees/{employeeId}/clock-in
- Given: employee exists and has no open shift
- Expect:
  - HTTP 200
  - status indicates CLOCKED_IN
  - shift_id returned
  - audit event recorded as CLOCK_IN_ACCEPTED
- Maps to: MVP-1

### API-2: Duplicate Clock-In Rejected
- Endpoint: POST /employees/{employeeId}/clock-in
- Given: employee already has open shift
- Expect:
  - HTTP 409
  - clear validation message
  - audit event recorded as CLOCK_IN_REJECTED
- Maps to: MVP-2

### API-3: Successful Clock-Out
- Endpoint: POST /employees/{employeeId}/clock-out
- Given: employee has open shift
- Expect:
  - HTTP 200
  - status indicates CLOCKED_OUT
  - duration_minutes > 0
  - audit event recorded as CLOCK_OUT_ACCEPTED
- Maps to: MVP-3

### API-4 (Optional if time remains): Payroll Summary Shape
- Endpoint: GET /employees/{employeeId}/payroll-summary
- Given: at least one closed shift
- Expect:
  - HTTP 200
  - total_minutes_worked present
  - closed_shift_count present
- Maps to: MVP-6

## 3. Minimum UI Test (Playwright TypeScript)

### UI-E2E-1: Main Path Clock-In to Clock-Out
- Setup:
  - run API and UI locally
  - use demo employee fixture
- Steps:
  1. open time-capture page
  2. select employee (or fixed demo employee)
  3. click Clock In
  4. verify status shows CLOCKED_IN
  5. click Clock Out
  6. verify status shows CLOCKED_OUT
  7. verify shift history or summary section updates
- Assertions:
  - user sees successful transitions
  - no uncaught UI errors
  - summary/history displays new shift row or updated totals
- Maps to: MVP-1, MVP-3, MVP-4

## 4. Highest-Risk Untested Behavior

- Clock-out rejection when no open shift exists may remain untested if API-4 is prioritized.
- Audit event content quality (details text semantics) may not be deeply validated.
- Timezone and boundary-time behavior (midnight crossings) is likely uncovered in MVP window.

## 5. Demo Evidence To Show

- API test run output proving pass/fail for the three minimum tests.
- Playwright run output or report for UI-E2E-1.
- one failure-path evidence artifact (duplicate punch rejection message).
- screenshot or log snippet showing updated shift summary/history after clock-out.

## 6. Smallest Sensible Testing Next Step

Implement API-1, API-2, API-3 immediately in code/tests/api and make them runnable with one command.
After API tests are green, add UI-E2E-1 in code/tests/e2e and run headless once for evidence.

## Suggested Commands

- API tests:
  - PYTHONPATH=$PWD/code python3 -m pytest code/tests/api -q
- Playwright tests (once configured):
  - npx playwright test --reporter=line
