# E2E Tests (Playwright)

This folder includes the required MVP main-path UI test:

- `specs/main-path.spec.ts`

## Run

1. Install dependencies:

	npm install

2. List tests:

	npm run test:list

3. Run tests:

	npm test

The Playwright config starts backend and frontend web servers automatically.

## Screenshot Archive

Each test run stores step screenshots under:

- `artifacts/playwright-runs/<run-id>/`

`<run-id>` is generated per run (timestamp-based) so the most recent run is always preserved separately.
