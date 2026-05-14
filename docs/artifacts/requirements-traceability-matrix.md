# Requirements Traceability Matrix

Date: 2026-05-14
Story Source: docs/artifacts/product-stories.md
Status Legend: Implemented, Partial, Not Started

| Epic | Story ID | Story | Current Contract / Endpoint | Test Coverage | Status |
|---|---|---|---|---|---|
| Workforce Time Management | WTM-1 | Employee Clock-In | POST /employees/{employee_id}/clock-in | API + E2E | Implemented |
| Workforce Time Management | WTM-2 | Employee Clock-Out | POST /employees/{employee_id}/clock-out | API + E2E | Implemented |
| Workforce Time Management | WTM-3 | Web Punch Management | UI punch actions in frontend + clock endpoints | E2E | Implemented |
| Workforce Time Management | WTM-4 | Mobile-Friendly Punch Workflows | Responsive UI + mobile punch flow | E2E (mobile spec) | Implemented |
| Workforce Time Management | WTM-5 | Punch Validation | Employee ID/date validation + duplicate/open-shift rejection | API | Implemented |
| Workforce Time Management | WTM-6 | Missing Punch Detection | GET /employees/{employee_id}/missing-punch-exceptions | API + UI | Implemented |
| Workforce Time Management | WTM-7 | Attendance Tracking | Shifts, payroll summary, and diagnostics read models | API + UI | Implemented |
| Workforce Time Management | WTM-8 | Time Correction Workflow | POST/GET /employees/{employee_id}/time-corrections | API | Implemented |
| Workforce Time Management | WTM-9 | Audit Logging | GET /employees/{employee_id}/audit-events | API + UI | Implemented |
| Scheduling and Leave Management | SLM-1 | Leave Request Workflow | POST /employees/{employee_id}/leave-requests | API | Implemented |
| Scheduling and Leave Management | SLM-2 | Leave Approval Workflow | POST /leave-requests/{leave_request_id}/approve | API | Implemented |
| Scheduling and Leave Management | SLM-3 | Leave Balance Tracking | GET /employees/{employee_id}/leave-balance | API | Implemented |
| Scheduling and Leave Management | SLM-4 | Shift Scheduling | POST/GET /employees/{employee_id}/scheduled-shifts | API | Implemented |
| Scheduling and Leave Management | SLM-5 | Break Enforcement | hard-fail validation on scheduled shift create against minimum break policy | API | Implemented |
| Scheduling and Leave Management | SLM-6 | Core-Hour Validation | hard-fail validation on scheduled shift create for configured core-hour coverage | API | Implemented |
| Scheduling and Leave Management | SLM-7 | Attendance Exception Handling | GET /employees/{employee_id}/attendance-exceptions | API | Implemented |
| Payroll and Compensation | PAY-1 | Online Timesheet Processing | GET /employees/{employee_id}/timesheets | API | Implemented |
| Payroll and Compensation | PAY-2 | Overtime Calculations | GET /employees/{employee_id}/payroll-breakdown (overtime_minutes) | API | Implemented |
| Payroll and Compensation | PAY-3 | Holiday Calculations | GET /employees/{employee_id}/payroll-breakdown (holiday_minutes) | API | Implemented |
| Payroll and Compensation | PAY-4 | Night-Shift Differential Calculations | GET /employees/{employee_id}/payroll-breakdown (night_shift_minutes) | API | Implemented |
| Payroll and Compensation | PAY-5 | PTO Management | GET /employees/{employee_id}/pto-balance + POST /employees/{employee_id}/pto-adjustments | API | Implemented |
| Payroll and Compensation | PAY-6 | Comp-Time Management | GET /employees/{employee_id}/comp-time-balance + POST /employees/{employee_id}/comp-time-adjustments | API | Implemented |
| Payroll and Compensation | PAY-7 | Payroll Export Processing | GET /companies/{company_id}/payroll-export | API | Implemented |
| Payroll and Compensation | PAY-8 | Payroll Integration Readiness | GET /companies/{company_id}/payroll-integration-payload | API | Implemented |
| Compliance and Reporting | CR-1 | Tax and Labor-Rule Validation Visibility | GET /employees/{employee_id}/compliance-report (skeleton) | API (limited) | Partial |
| Compliance and Reporting | CR-2 | Compliance Reporting | GET /employees/{employee_id}/compliance-report | API | Partial |
| Compliance and Reporting | CR-3 | Attendance Exception Reporting | GET /employees/{employee_id}/attendance-exceptions | API | Implemented |
| Compliance and Reporting | CR-4 | Audit Trail Reporting | GET /employees/{employee_id}/audit-events | API + UI | Implemented |
| Compliance and Reporting | CR-5 | Operational Reporting | GET /reports/operational + GET /ops/diagnostics | API | Implemented |
| Compliance and Reporting | CR-6 | CrossCheck Reporting | GET /reports/crosscheck | API | Implemented |
| Mobile Workforce Support | MWS-1 | Mobile-Friendly Workflows | Responsive layout and mobile viewport flow | E2E (mobile spec) | Implemented |
| Mobile Workforce Support | MWS-2 | Mobile Punch Support | Mobile browser punch through same API contracts | E2E (mobile spec) | Implemented |
| Mobile Workforce Support | MWS-3 | Responsive UI Behavior | CSS responsive behavior in frontend | Indirect (UI) | Implemented |
| Mobile Workforce Support | MWS-4 | Device Accessibility Support | Accessibility test pack added for landmarks, labels, status semantics, skip-link, and keyboard flow | E2E | Implemented |
| Enterprise Readiness | ENT-1 | Multi-Company Workflows | GET /companies/{company_id}/employees + company-scoped payroll endpoints | API | Implemented |
| Enterprise Readiness | ENT-2 | Multi-Location Workflows | GET /companies/{company_id}/locations, GET /companies/{company_id}/locations/{location_id}/employees, GET /companies/{company_id}/locations/{location_id}/payroll-export | API | Implemented |
| Enterprise Readiness | ENT-3 | Policy Configurability | GET /policies + PATCH /policies (admin-guarded) | API | Implemented |
| Enterprise Readiness | ENT-4 | Role-Based Access Control | Header-based role checks + POST /authz/check | API | Implemented |
| Enterprise Readiness | ENT-5 | Enterprise Scalability Considerations | API-first DB-backed service; some process-memory state still present | Architectural | Partial |

## Summary

- Total stories tracked: 39
- Implemented: 36
- Partial: 3
- Not Started: 0

## Remaining Gaps (Exact)

- CR-1 and CR-2 compliance/tax/labor status is currently simplified summary output.
- ENT-5 still includes selected in-process state (policy and adjustment collections), limiting horizontal scaling semantics.

## Technical Requirement 5.1 (API-First Design)

- Covered: frontend web app, mobile browser workflows, and integration-facing contracts are all API-backed.
- Covered contracts: employee workflows, company payroll exports, and integration payload endpoint.
