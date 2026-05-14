# Demo-Ready Checklist

Date: 2026-05-14

## UI Demo Flow

- [x] App starts reliably (backend and frontend)
- [x] Clock-in works live
- [x] Duplicate or invalid punch case is visible
- [x] Clock-out works live
- [x] Shift history or summary updates live
- [x] Leave request and approval flow is visible in the UI
- [x] Scheduling workflow is visible in the UI
- [x] Payroll breakdown and compliance report are visible in the UI
- [x] Missing punch visibility is present in the UI
- [x] Mobile and accessibility baseline can be demonstrated

## API And Evidence

- [x] Audit logging is visible in UI
- [x] Payroll summary is visible in UI
- [x] API tests can be shown for the broader contract surface
- [x] Playwright suite can be shown for main path, accessibility, and mobile baseline
- [x] Company/location, leave, scheduling, payroll, and reporting APIs exist for demo-by-endpoint walkthroughs

## Narrative And Honesty

- [x] The source-of-truth requirements are referenced
- [x] API-backed features are distinguished from UI-backed features
- [x] Known partial areas are stated explicitly: demo auth stub, local SQLite dev defaults, missing enterprise-admin UI, minimal downstream alert routing, and missing event-driven integration

## Notes

Use this file as the final current-state pre-demo gate before presenting.
