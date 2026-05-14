# Quick Reference

## Core Endpoints
- POST /employees/{employeeId}/clock-in
- POST /employees/{employeeId}/clock-out
- GET /employees/{employeeId}/shifts
- GET /employees/{employeeId}/audit-events
- GET /employees/{employeeId}/payroll-summary

## Required Behaviors
- Reject duplicate open clock-ins
- Reject clock-out when no open shift exists
- Persist audit events for success and rejection
