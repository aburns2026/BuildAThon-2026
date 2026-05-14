# Developer Contract-First Outcome (Current State)

Date: 2026-05-14
Stack: FastAPI + React + Playwright TypeScript

## Implemented Domain Model

### Durable Database-Backed Entities
- Employee
- Shift
- AuditEvent
- LeaveRequest
- ScheduledShift
- TimeCorrection
- PtoAdjustment
- CompTimeAdjustment
- PolicySetting

### Current In-Process Runtime State
- request metrics counters

## Implemented Contract Surface

### Time Capture And Visibility
- POST /employees/{employeeId}/clock-in
- POST /employees/{employeeId}/clock-out
- GET /employees/{employeeId}/shifts
- GET /employees/{employeeId}/audit-events
- GET /employees/{employeeId}/payroll-summary
- GET /employees/{employeeId}/missing-punch-exceptions

### Scheduling, Leave, And Exceptions
- POST/GET /employees/{employeeId}/time-corrections
- POST/GET /employees/{employeeId}/leave-requests
- POST /leave-requests/{leaveRequestId}/approve
- GET /employees/{employeeId}/leave-balance
- POST/GET /employees/{employeeId}/scheduled-shifts
- GET /employees/{employeeId}/attendance-exceptions

### Payroll, Reporting, And Enterprise Contracts
- GET /employees/{employeeId}/compliance-report
- GET /employees/{employeeId}/timesheets
- GET /employees/{employeeId}/payroll-breakdown
- GET /employees/{employeeId}/pto-balance
- POST /employees/{employeeId}/pto-adjustments
- GET /employees/{employeeId}/comp-time-balance
- POST /employees/{employeeId}/comp-time-adjustments
- GET /companies/{companyId}/employees
- GET /companies/{companyId}/locations
- GET /companies/{companyId}/locations/{locationId}/employees
- GET /companies/{companyId}/payroll-export
- GET /companies/{companyId}/locations/{locationId}/payroll-export
- GET /companies/{companyId}/payroll-integration-payload
- GET /reports/operational
- GET /reports/crosscheck
- GET /policies
- PATCH /policies
- POST /authz/check
- GET /ops/diagnostics
- GET /metrics

## Implemented UI Surface

The React UI currently exposes:

- punch controls
- status messaging
- shift history
- payroll summary
- payroll breakdown
- compliance report
- leave request and approval flow
- scheduling workflow
- leave balance visibility
- audit event list
- missing punch exception list
- responsive and accessibility baseline behavior

## Current Technical Debt

- Local development still defaults to file-backed SQLite, and runtime telemetry counters remain instance-local.
- The frontend still does not represent enterprise admin workflows or broader reporting views.

## Recommended Next Development Step

Expand the frontend for enterprise-admin or broader reporting workflows, or wire the alerting stack to real downstream receivers and secret-management boundaries.
