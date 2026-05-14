# Demo-Ready Checklist

Date: 2026-05-14

## Core Flow

- [x] App starts reliably (backend and frontend)
- [x] Clock-in works live
- [x] Duplicate or invalid punch case is visible
- [x] Clock-out works live
- [x] Shift history or summary updates live

## Evidence and Visibility

- [x] Audit logging is visible in UI
- [x] Payroll summary is visible in UI
- [x] API tests can be shown (`python3 -m pytest code/tests/api -q`)
- [x] Playwright main-path test can be shown (`npm test` in `code/tests/e2e`)

## Scope and Narrative

- [x] Deferred scope is explicit and honest
- [x] MVP scope lock is referenced
- [x] Explainable demo story from clock-in to payroll summary

## Notes

Use this file as the final pre-demo gate before presenting.
