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
- audit events
- missing punch exception visibility
- responsive/mobile baseline behavior
- accessibility baseline behavior

The remaining broader operational reporting and enterprise workflows are currently API-backed only and do not yet have React views.

## Run

1. Install deps:

	npm install

2. Start backend in another terminal from `code/backend`:

	uvicorn main:app --reload --host 0.0.0.0 --port 8000

3. Start frontend:

	npm run dev -- --host 0.0.0.0 --port 5173

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

## Container

This frontend can also be built through the repository root `docker-compose.yml`, which now starts a PostgreSQL-backed backend service alongside the frontend and external monitoring services.
