# Frontend (React)

This frontend is the current browser-facing slice of the platform.

Implemented UI coverage:

- clock-in
- clock-out
- shift history
- payroll summary
- payroll breakdown visibility
- compliance report visibility
- leave request submission
- leave approval
- leave balance visibility
- shift scheduling workflow
- enterprise admin company directory and location coverage
- editable policy controls and employee location reassignment
- stubbed downstream notification configuration and test trigger
- stubbed secret-provider configuration using reference names only
- operational reporting, crosscheck summary, payroll export readiness, and location-scoped payroll export views
- PTO balance and PTO adjustments
- comp-time balance and comp-time adjustments
- payroll integration payload visibility
- audit events
- missing punch exception visibility
- responsive/mobile baseline behavior
- accessibility baseline behavior

The remaining broader admin actions and deeper enterprise workflows are still primarily API-backed, and notification/secret support is still stubbed rather than backed by real providers.

API-only surfaces outside the current browser demo:

- authz check
- ops diagnostics

## Run

1. Install deps:

	npm install

2. Start backend in another terminal from `code/backend`:

	RESET_DATABASE_ON_STARTUP=1 ENABLE_DEMO_RESET_ENDPOINTS=1 DEMO_RESET_TOKEN=demo-reset uvicorn main:app --reload --host 0.0.0.0 --port 8000

3. Start frontend:

	npm run dev -- --host 0.0.0.0 --port 5173

4. Run frontend unit tests:

	npm test

The backend command above forces a clean demo boot so the browser starts from empty shift, leave, and audit state. To reset a running local demo without restarting the backend:

```bash
curl -X POST http://127.0.0.1:8000/demo-support/reset -H 'x-demo-reset-token: demo-reset'
```

## API Base URL

By default, UI calls `http://127.0.0.1:8000`.

Set a custom API base with:

```bash
VITE_API_BASE=http://127.0.0.1:8000 npm run dev -- --host 0.0.0.0 --port 5173
```

## Demo Auth Token

The frontend sends a bearer token with each request.

Default token:

- `demo-employee-token`

Manager token used for leave approval and scheduling in the UI:

- `demo-manager-token`

Override it with:

```bash
VITE_DEMO_AUTH_TOKEN=demo-employee-token npm run dev -- --host 0.0.0.0 --port 5173
```

To override the manager token used by the leave-approval path:

```bash
VITE_MANAGER_AUTH_TOKEN=demo-manager-token npm run dev -- --host 0.0.0.0 --port 5173
```

For runtime browser testing, the app also honors these `localStorage` overrides if they are present before page load:

- `buildathon.demoAuthToken`
- `buildathon.managerAuthToken`
- `buildathon.payrollAuthToken`
- `buildathon.adminAuthToken`

## Container

This frontend can also be built through the repository root `docker-compose.yml`, which now starts a PostgreSQL-backed backend service alongside the frontend and external monitoring services.
