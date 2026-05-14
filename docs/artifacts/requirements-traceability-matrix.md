# Requirements Traceability Matrix

Date: 2026-05-14
Story Source: docs/artifacts/product-stories.md
Status Legend: Implemented, Partial, Not Started

| Area | Story ID | Story | Delivery Surface | Current Implementation | Evidence | Status |
|---|---|---|---|---|---|---|
| Workforce Time Management | WTM-1 | Employee Clock-In | API + UI | POST /employees/{employee_id}/clock-in and frontend punch flow | API tests + Playwright | Implemented |
| Workforce Time Management | WTM-2 | Employee Clock-Out | API + UI | POST /employees/{employee_id}/clock-out and frontend punch flow | API tests + Playwright | Implemented |
| Workforce Time Management | WTM-3 | Web Punch Management | API + UI | Browser-based punch controls backed by clock endpoints | Playwright | Implemented |
| Workforce Time Management | WTM-4 | Mobile-Friendly Punch Workflows | API + UI | Responsive frontend and mobile viewport punch flow | Playwright mobile | Implemented |
| Workforce Time Management | WTM-5 | Punch Validation | API | Employee ID validation, duplicate clock-in rejection, no-open-shift clock-out rejection | API tests | Implemented |
| Workforce Time Management | WTM-6 | Missing Punch Detection | API + UI | GET /employees/{employee_id}/missing-punch-exceptions and exceptions card in frontend | API tests + UI | Implemented |
| Workforce Time Management | WTM-7 | Attendance Tracking | API + UI | GET /employees/{employee_id}/shifts, GET /employees/{employee_id}/payroll-summary, and diagnostics read models | API tests + Playwright | Implemented |
| Workforce Time Management | WTM-8 | Time Correction Workflow | API only | POST/GET /employees/{employee_id}/time-corrections | API tests | Implemented |
| Workforce Time Management | WTM-9 | Audit Logging | API + UI | GET /employees/{employee_id}/audit-events and audit section in frontend | API tests + Playwright | Implemented |
| Scheduling and Leave Management | SLM-1 | Leave Request Workflow | API + UI | POST /employees/{employee_id}/leave-requests, GET /employees/{employee_id}/leave-requests, and leave-request form in frontend | API tests + Playwright | Implemented |
| Scheduling and Leave Management | SLM-2 | Leave Approval Workflow | API + UI | POST /leave-requests/{leave_request_id}/approve and manager-approval action in frontend | API tests + Playwright | Implemented |
| Scheduling and Leave Management | SLM-3 | Leave Balance Tracking | API + UI | GET /employees/{employee_id}/leave-balance and leave-balance summary in frontend | API tests + Playwright | Implemented |
| Scheduling and Leave Management | SLM-4 | Shift Scheduling | API + UI | POST/GET /employees/{employee_id}/scheduled-shifts plus manager scheduling form and scheduled-shift list in frontend | API tests + Playwright | Implemented |
| Scheduling and Leave Management | SLM-5 | Break Enforcement | API only | Scheduled shift creation enforces minimum_break_minutes policy | API tests | Implemented |
| Scheduling and Leave Management | SLM-6 | Core-Hour Validation | API only | Scheduled shift creation enforces configured core-hour coverage | API tests | Implemented |
| Scheduling and Leave Management | SLM-7 | Attendance Exception Handling | API only | GET /employees/{employee_id}/attendance-exceptions aggregates missing-punch and policy violations | API tests | Implemented |
| Payroll and Compensation | PAY-1 | Online Timesheet Processing | API only | GET /employees/{employee_id}/timesheets | API tests | Implemented |
| Payroll and Compensation | PAY-2 | Overtime Calculations | API + UI | GET /employees/{employee_id}/payroll-breakdown returns overtime_minutes and frontend payroll-breakdown card surfaces the value | API tests + Playwright | Implemented |
| Payroll and Compensation | PAY-3 | Holiday Calculations | API + UI | GET /employees/{employee_id}/payroll-breakdown returns holiday_minutes and frontend payroll-breakdown card surfaces the value | API tests + Playwright | Implemented |
| Payroll and Compensation | PAY-4 | Night-Shift Differential Calculations | API + UI | GET /employees/{employee_id}/payroll-breakdown returns night_shift_minutes and frontend payroll-breakdown card surfaces the value | API tests + Playwright | Implemented |
| Payroll and Compensation | PAY-5 | PTO Management | API only | GET /employees/{employee_id}/pto-balance and POST /employees/{employee_id}/pto-adjustments | API tests | Implemented |
| Payroll and Compensation | PAY-6 | Comp-Time Management | API only | GET /employees/{employee_id}/comp-time-balance and POST /employees/{employee_id}/comp-time-adjustments | API tests | Implemented |
| Payroll and Compensation | PAY-7 | Payroll Export Processing | API only | GET /companies/{company_id}/payroll-export and location-scoped export | API tests | Implemented |
| Payroll and Compensation | PAY-8 | Payroll Integration Readiness | API only | GET /companies/{company_id}/payroll-integration-payload | API tests | Implemented |
| Compliance and Reporting | CR-1 | Tax and Labor-Rule Validations | API + UI | GET /employees/{employee_id}/compliance-report evaluates tax reconciliation, employee assignment, attendance exceptions, open shifts, and shift-duration guardrails, and the frontend compliance card surfaces those validations | API tests + Playwright | Implemented |
| Compliance and Reporting | CR-2 | Compliance Reporting | API + UI | GET /employees/{employee_id}/compliance-report returns rolled-up statuses plus detailed tax and labor validation results in both API and frontend compliance views | API tests + Playwright | Implemented |
| Compliance and Reporting | CR-3 | Attendance Exception Reporting | API only | GET /employees/{employee_id}/attendance-exceptions | API tests | Implemented |
| Compliance and Reporting | CR-4 | Audit Trail Reporting | API + UI | GET /employees/{employee_id}/audit-events and audit history in frontend | API tests + Playwright | Implemented |
| Compliance and Reporting | CR-5 | Operational Reporting | API only | GET /reports/operational and GET /ops/diagnostics | API tests | Implemented |
| Compliance and Reporting | CR-6 | CrossCheck Reporting | API only | GET /reports/crosscheck | API tests | Implemented |
| Mobile Workforce Support | MWS-1 | Mobile-Friendly Workflows | UI | Responsive time-capture console | Playwright mobile | Implemented |
| Mobile Workforce Support | MWS-2 | Mobile Punch Support | API + UI | Mobile browser punch flow using the same API contracts | Playwright mobile | Implemented |
| Mobile Workforce Support | MWS-3 | Responsive UI Behavior | UI | Frontend responsive layout and controls | Playwright mobile | Implemented |
| Mobile Workforce Support | MWS-4 | Device Accessibility Support | UI | Skip link, accessible names, status live region, keyboard flow, and landmark coverage | Playwright accessibility | Implemented |
| Enterprise Readiness | ENT-1 | Multi-Company Workflows | API only | GET /companies/{company_id}/employees and company-scoped payroll endpoints | API tests | Implemented |
| Enterprise Readiness | ENT-2 | Multi-Location Workflows | API only | GET /companies/{company_id}/locations, location employee listing, and location payroll export | API tests | Implemented |
| Enterprise Readiness | ENT-3 | Policy Configurability | API only | GET /policies and PATCH /policies with admin guardrails | API tests | Implemented |
| Enterprise Readiness | ENT-4 | Role-Based Access Control | API only | Bearer-token auth stub, principal-bound role checks, and POST /authz/check | API tests | Implemented |
| Enterprise Readiness | ENT-5 | Enterprise Scalability Considerations | Architecture | Workflow and policy state are DB-backed and the containerized runtime uses PostgreSQL, but local development still defaults to file-backed SQLite and request counters are instance-local | Code review | Partial |
| Technical Architecture and Integration Readiness | TAR-1 | Web Application API Support | API + UI | React frontend consumes backend HTTP contracts | Code review + Playwright | Implemented |
| Technical Architecture and Integration Readiness | TAR-2 | Mobile Application API Support | API + UI | Same HTTP contracts drive mobile browser workflows | Code review + Playwright mobile | Implemented |
| Technical Architecture and Integration Readiness | TAR-3 | Enterprise Integration API Support | API only | Payroll export and payroll integration payload endpoints | API tests | Implemented |
| Technical Architecture and Integration Readiness | TAR-4 | Future Extensibility by API Design | Architecture | API-first contract surface exists, but extension posture is still lightweight | Code review | Partial |
| Technical Architecture and Integration Readiness | TAR-5 | Stateless Service Alignment | Architecture | Core workflow and policy state are DB-backed and the containerized path is PostgreSQL-backed, but local development still defaults to file-backed SQLite and telemetry counters are instance-local | Code review | Partial |
| Technical Architecture and Integration Readiness | TAR-6 | API-Based Communication | Architecture | Frontend, tests, and integration flows all communicate through HTTP APIs | Code review | Implemented |
| Technical Architecture and Integration Readiness | TAR-7 | Container-Ready Architecture | Architecture | Backend and frontend Dockerfiles plus root docker-compose.yml provide a containerized run path | Repo inspection + docker build | Implemented |
| Technical Architecture and Integration Readiness | TAR-8 | Secure Secret Management | Architecture | Environment variables are supported, but no dedicated secret-management integration exists | Code review | Partial |
| Technical Architecture and Integration Readiness | TAR-9 | Observability Support | Architecture | /health, /ops/diagnostics, /metrics, request-id correlation, request counters, and external Prometheus/Grafana assets provide an observability baseline | Code review + API tests + config validation | Implemented |
| Technical Architecture and Integration Readiness | TAR-10 | Logging and Monitoring Support | Architecture | Request logging middleware, x-request-id correlation, diagnostics counters, `/metrics`, Prometheus alert rules, Alertmanager, and Grafana dashboard provisioning provide monitoring support | Code review + API tests + config validation | Implemented |
| Technical Architecture and Integration Readiness | TAR-11 | Future CIAM Integration Readiness | Architecture | Bearer-token auth stub creates an auth boundary, but no CIAM integration exists | Code review | Partial |
| Technical Architecture and Integration Readiness | TAR-12 | Future Enterprise Domain Integration Readiness | Architecture | Company/location scoping and integration payload contracts provide a baseline only | Code review + API tests | Partial |
| Technical Architecture and Integration Readiness | TAR-13 | Future Event-Driven Integration Readiness | Architecture | No event contracts or messaging assets are present | Repo inspection | Not Started |
| Technical Architecture and Integration Readiness | TAR-14 | Future Cloud-Native Extensibility | Architecture | API-first backend, migrations, and diagnostics exist, but runtime cloud-native posture is incomplete | Code review | Partial |

## Summary

- Total stories tracked: 53
- Implemented: 45
- Partial: 7
- Not Started: 1

## Remaining Gaps (Exact)

- ENT-5 and TAR-5 remain partial because local development still defaults to file-backed SQLite and request counters remain instance-local even though workflow and policy state are durable.
- TAR-13 is not started because no event-driven integration contract exists yet.

## Notes On Delivery Surface

- Functional breadth is strongest at the API layer.
- The frontend currently covers time capture, leave and scheduling basics, payroll detail, compliance reporting basics, missing-punch visibility, and accessibility/mobile baselines.
- Enterprise admin workflows and broader operational/company reporting remain API-only.
