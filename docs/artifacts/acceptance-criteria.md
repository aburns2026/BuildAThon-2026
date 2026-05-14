# Acceptance Criteria (Current State)

Date: 2026-05-14
Source alignment:

- docs/bbsi_buildathon_2026_requirements_only.md sections 4 and 5
- docs/artifacts/product-stories.md

## Workforce Time Management

- Given a valid employee with no open shift, when clock-in is submitted, then an open shift is created and an accepted audit event is stored.
- Given an employee with an open shift, when another clock-in is submitted, then the request is rejected with a safe validation message and a rejected audit event.
- Given an employee with an open shift, when clock-out is submitted, then the open shift is closed, duration is computed, and an accepted audit event is stored.
- Given an employee with recorded shifts, when shifts or payroll summary are requested, then the response includes current attendance and worked-time totals.
- Given an open shift older than the configured threshold, when missing punch exceptions are requested, then the response includes a missing-punch exception entry.
- Given a browser user on desktop or mobile, when the punch flow is used, then status messaging, responsive layout, and accessible interactions remain usable.

## Scheduling and Leave Management

- Given valid leave dates, when a leave request is submitted, then the request is stored with pending status.
- Given a pending leave request, when manager approval is submitted, then the request status becomes approved.
- Given approved leave, when leave balance is requested, then used and remaining totals are returned.
- Given a valid scheduled shift payload, when the shift is created, then it is retrievable for the employee.
- Given a scheduled shift that violates minimum break policy or configured core hours, when creation is attempted, then the request is rejected with an explicit validation message.
- Given scheduled shift policy violations or missing punch cases, when attendance exceptions are requested, then the response returns unified exception records.

## Payroll and Compensation

- Given closed shifts within a requested period, when timesheets are requested, then line-item entries and total minutes are returned.
- Given closed shifts, when payroll breakdown is requested, then regular, overtime, holiday, and night-shift minutes are returned.
- Given approved time-off or manager adjustments, when PTO and comp-time balances are requested, then current totals reflect stored adjustments.
- Given payroll export or payroll integration payload requests, when authorized users call company-scoped endpoints, then stable export-ready payloads are returned.

## Compliance, Reporting, and Enterprise Controls

- Given attendance exception and audit data, when operational or crosscheck reports are requested, then the service returns deterministic aggregate or reconciliation output.
- Given a compliance report request, when the endpoint is called, then the response returns validation-status fields and attendance exception count.
- Given protected endpoints, when authorization headers are missing or invalid, then the request is rejected safely.
- Given company-scoped endpoints, when the company claim is missing or mismatched, then the request is rejected safely.
- Given policy changes, when a non-admin caller attempts to patch policies, then the request is rejected.

## Technical Requirement Acceptance Criteria

- Given web and mobile browser clients, when they call the backend, then the workflow contracts are API-backed and reusable across clients.
- Given current runtime posture, when health or diagnostics are requested, then baseline operational endpoints respond successfully.
- Given current architecture, when delivery claims are reviewed, then remaining gaps are explicit: real compliance logic, durable state for selected in-memory collections, container packaging, and logging/monitoring support.
