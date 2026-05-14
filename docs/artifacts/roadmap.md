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

## Phase 2 (Completed): Functional Requirement Expansion

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
- [x] Tax and labor-rule validations
- [x] Compliance reporting
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
- [x] Enterprise scalability considerations (baseline only; core workflow state persisted, but policy/runtime scaling remains limited)

## Phase 3 (Current): Documentation And Technical Readiness Alignment

- [x] Refresh planning, stories, and traceability to match the implemented repo
- [x] Reframe MVP-first artifacts so they describe current state honestly
- [x] Persist in-memory time correction and adjustment state
- [x] Add container-ready assets
- [x] Add baseline application logging and request correlation support
- [x] Expand the frontend beyond time capture for API-backed workflows
- [x] Expand beyond leave into payroll-detail and compliance UI
- [x] Add API metrics and a PostgreSQL-backed compose configuration
- [x] Expand into scheduling UI
- [x] Move policy configuration to durable storage and add external alerting/monitoring
- [ ] Expand into enterprise-admin UI and broader reporting views
- [ ] Add downstream notification integrations and stronger secret-management support

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
17. Replaced placeholder compliance PASS values with rule-based tax and labor validations.
18. Added API coverage for compliance fail-state evaluation.
19. Verification: focused compliance tests passed.
20. Persisted time corrections, PTO adjustments, and comp-time adjustments to database tables.
21. Added a leave workflow UI with request, approval, and balance visibility.
22. Added request logging, request-id correlation, Dockerfiles, and docker-compose support.
23. Verification: full API suite 36 passed, full Playwright suite 6 passed, backend coverage 90%, backend/frontend images built.
24. Added frontend payroll-breakdown and compliance-report views to the demo UI.
25. Added `/metrics`, richer health/diagnostics reporting, psycopg support, and a PostgreSQL-backed compose configuration.
26. Verification: full API suite 37 passed, full Playwright suite 6 passed, backend coverage 90%, compose config validated.
27. Persisted policy configuration in the database and removed `POLICY_CONFIG` as the runtime source of truth.
28. Added a manager-visible scheduling workflow to the frontend and Playwright coverage for it.
29. Added Prometheus, Alertmanager, and Grafana configuration for external dashboarding and alert evaluation.
30. Verification: full API suite 37 passed, full Playwright suite 7 passed, backend coverage 90%, compose and monitoring configs validated.

## Implementation Order (Next)
1. Expand the frontend for enterprise-admin and broader reporting workflows.
2. Add downstream alert receivers and stronger secret-management support.
3. Add future integration posture for event-driven readiness if that becomes a target.

## Definition Of Done For This Phase
- Each current-state claim in docs is backed by code, tests, or explicit gap notes.
- Traceability matrix status remains aligned to the source-of-truth requirements.
- Roadmap checkboxes are only marked complete when the repository evidence supports them.
