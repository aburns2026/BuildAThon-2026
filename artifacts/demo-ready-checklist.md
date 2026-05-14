# Demo-Ready Checklist

Date: 2026-05-14

## Core Flow

- [ ] App starts reliably (backend and frontend)
- [ ] Clock-in works live
- [ ] Duplicate or invalid punch case is visible
- [ ] Clock-out works live
- [ ] Shift history or summary updates live

## Evidence and Visibility

- [ ] Audit logging is visible in UI
- [ ] Payroll summary is visible in UI
- [ ] API tests can be shown (`python3 -m pytest code/tests/api -q`)
- [ ] Playwright main-path test can be shown (`npm test` in `code/tests/e2e`)

## Scope and Narrative

- [ ] Deferred scope is explicit and honest
- [ ] MVP scope lock is referenced
- [ ] Explainable demo story from clock-in to payroll summary

## Notes

Use this file as the final pre-demo gate before presenting.
