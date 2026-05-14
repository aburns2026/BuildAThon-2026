# Product Roadmap (Requirements-Aligned)

Date: 2026-05-14

## Phase 0 (Completed): MVP Foundation
- Time capture core: clock-in/out, shift history, audit events, payroll summary
- QA baseline: API tests + one Playwright main-path flow with screenshots
- Security baseline: input validation hardening and verifier review
- Support baseline: triage workflow and diagnostics notes

## Phase 1 (Completed): Initial Expansion
- Missing punch detection and exception visibility
- Leave request/approval/balance baseline
- Scheduled shifts baseline
- Payroll breakdown and compliance report skeleton
- Enterprise employee listing and ops diagnostics

## Phase 2 (Executed): Remaining Requirement Features

### Epic: Workforce Time Management
- [x] Employee clock-in workflows
- [x] Employee clock-out workflows
- [x] Web-based punch management
- [x] Mobile-friendly punch workflows
- [x] Punch validation
- [x] Missing punch detection
- [x] Attendance tracking
- [x] Employee time correction workflows
- [x] Audit logging

### Epic: Scheduling & Leave Management
- [x] Leave request workflows
- [x] Leave approval workflows
- [x] Leave balance tracking
- [x] Shift scheduling
- [x] Break enforcement
- [x] Core-hour validation
- [x] Attendance exception handling

### Epic: Payroll & Compensation
- [x] Online timesheet processing
- [x] Overtime calculations
- [x] Holiday calculations
- [x] Night-shift differential calculations
- [x] PTO management
- [x] Comp-time management
- [x] Payroll export processing
- [x] Payroll integration readiness

### Epic: Compliance & Reporting
- [x] Tax and labor-rule validations (baseline skeleton)
- [x] Compliance reporting (baseline skeleton)
- [x] Attendance exception reporting (baseline via missing punch)
- [x] Audit trails
- [x] Operational reporting (expanded)
- [x] CrossCheck reporting

### Epic: Mobile Workforce Support
- [x] Mobile-friendly workflows
- [x] Mobile punch support
- [x] Responsive UI behavior
- [x] Device accessibility support (baseline)

### Epic: Enterprise Readiness
- [x] Multi-company workflows (baseline)
- [x] Multi-location workflows (baseline model)
- [x] Policy configurability
- [x] Role-based access control (endpoint-level enforcement on sensitive routes)
- [x] Enterprise scalability considerations (API-first/stateless baseline)

## Execution Log
1. Implemented break/core-hour enforcement metadata in scheduled shifts.
2. Implemented attendance exceptions contract.
3. Implemented timesheets, overtime, holiday, and night-shift calculations.
4. Implemented PTO and comp-time balance and adjustment contracts.
5. Implemented payroll export and payroll integration payload contracts.
6. Implemented operational and crosscheck reporting contracts.
7. Implemented policy configuration and role authorization-check contract.
8. Added API tests for phase-2 contracts and re-ran suite.
9. Verification: 27 API tests passed, backend coverage 93%.
10. Implemented baseline UI accessibility upgrades (skip link, live region messaging, focus-visible styles).
11. Added mobile-first Playwright coverage for responsive/accessibility baseline.
12. Stabilized existing Playwright selectors for repeated-state runs and strict mode.
13. Verification: Playwright suite 2 passed, 0 failed.
14. Implemented endpoint-level role authorization enforcement using `X-Role` header on protected endpoints.
15. Added RBAC enforcement tests and updated affected API tests.
16. Verification: API suite 27 passed, 0 failed.

## Implementation Order (Next)
1. Expand multi-location contracts beyond employee model field into location-scoped endpoints.
2. Refresh acceptance criteria and validation-rules docs to match phase-2 delivery.
3. Evaluate transition from in-memory stores to persistent database-backed contracts.

## Definition Of Done For This Phase
- Each new feature has an API contract in backend
- Each feature has at least one API test
- Traceability matrix status is updated
- Roadmap checklist item is checked only after tests pass
