# Quick Reference

## Auth Defaults

- Bearer token: `demo-employee-token`
- Manager token: `demo-manager-token`
- Payroll token: `demo-payroll-token`
- Admin token: `demo-admin-token`

## Core UI-Backed Endpoints

- POST /employees/{employeeId}/clock-in
- POST /employees/{employeeId}/clock-out
- GET /employees/{employeeId}/shifts
- GET /employees/{employeeId}/audit-events
- GET /employees/{employeeId}/payroll-summary
- GET /employees/{employeeId}/payroll-breakdown
- GET /employees/{employeeId}/compliance-report
- GET /employees/{employeeId}/missing-punch-exceptions
- POST /employees/{employeeId}/leave-requests
- GET /employees/{employeeId}/leave-requests
- POST /leave-requests/{leaveRequestId}/approve
- GET /employees/{employeeId}/leave-balance
- POST /employees/{employeeId}/scheduled-shifts
- GET /employees/{employeeId}/scheduled-shifts

## Expanded API Surface

- POST/GET /employees/{employeeId}/time-corrections
- POST/GET /employees/{employeeId}/leave-requests
- POST /leave-requests/{leaveRequestId}/approve
- GET /employees/{employeeId}/leave-balance
- POST/GET /employees/{employeeId}/scheduled-shifts
- GET /employees/{employeeId}/attendance-exceptions
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

## Required Behaviors
- Reject duplicate open clock-ins
- Reject clock-out when no open shift exists
- Persist audit events for success and rejection
- Require bearer auth on non-health endpoints
- Require matching company claims on company-scoped endpoints
- Return `x-request-id` on API responses for request correlation

## Container Commands

- Validate compose: `docker compose config`
- Start stack: `docker compose up --build`
- Compose now starts `postgres`, `backend`, `frontend`, `prometheus`, `alertmanager`, and `grafana` together for the containerized demo path.
