# MVP Stories (PO/BA)

## Scope Guard
These stories are limited to the 4-hour MVP time-capture slice.

## Story MVP-1: Clock-In
As an employee, I want to clock in so my workday start is recorded.

### Value
Creates the official start record for a shift and enables downstream payroll summary.

## Story MVP-2: Duplicate Clock-In Prevention
As the system, I need to reject duplicate open clock-ins so shift data remains valid.

### Value
Prevents overlapping or inconsistent shift records.

## Story MVP-3: Clock-Out
As an employee, I want to clock out so my workday end is recorded and duration is calculated.

### Value
Completes the shift record and supports payroll-ready summaries.

## Story MVP-4: Shift History or Today Summary
As an employee, I want to view my recent shifts or today summary so I can verify recorded time.

### Value
Provides transparency and confidence in captured time.

## Story MVP-5: Audit Visibility
As a manager or reviewer, I want audit events for punch actions so I can trace activity and validation outcomes.

### Value
Improves accountability and troubleshooting during demo and review.

## Story MVP-6: Payroll-Ready Summary
As payroll operations, I want a per-employee worked-time summary so I can use time data for downstream payroll processing.

### Value
Demonstrates payroll integration readiness without implementing a full payroll engine.
