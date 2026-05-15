# E2E Tests (Playwright)

This folder includes the current Playwright coverage for the frontend slice:

- `specs/main-path.spec.ts`
- `specs/accessibility-pack.spec.ts`
- `specs/mobile-accessibility.spec.ts`
- `specs/leave-workflow.spec.ts`
- `specs/scheduling-workflow.spec.ts`
- `specs/negative-paths.spec.ts`
- `specs/admin-reporting.spec.ts`

Current evidence snapshot:

- 13 passing tests
- screenshot archiving under `artifacts/playwright-runs/<run-id>/`
- automatic backend and frontend startup through Playwright config
- per-test backend reset through a test-support endpoint and isolated Playwright database

The admin/reporting spec now covers simple editable management flows as well: policy updates, employee location reassignment, notification-stub configuration/testing, and secret-provider stub configuration.

The browser suite intentionally does not claim coverage for API-only enterprise surfaces such as `/authz/check` or `/ops/diagnostics`.

Before a demo, run the repository `test_runner` from the workspace root:

```bash
./scripts/test_runner.sh
```

## Run

1. Install dependencies:

	npm install

2. List tests:

	npm run test:list

3. Run tests:

	npm test

4. Run a single spec if needed:

	npx playwright test specs/main-path.spec.ts

The Playwright config starts backend and frontend web servers automatically.

## Screenshot Archive

Each test run stores step screenshots under:

- `artifacts/playwright-runs/<run-id>/`

`<run-id>` is generated per run (timestamp-based) so the most recent run is always preserved separately.
