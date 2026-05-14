# Frontend (React)

This frontend is a thin MVP console for:

- clock-in
- clock-out
- shift history
- audit events
- payroll summary

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

VITE_API_BASE=http://127.0.0.1:8000 npm run dev -- --host 0.0.0.0 --port 5173
