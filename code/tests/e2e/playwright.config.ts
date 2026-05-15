import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./specs",
  timeout: 60_000,
  retries: 0,
  workers: 1,
  use: {
    baseURL: "http://127.0.0.1:5173",
    trace: "on-first-retry",
    screenshot: "on",
    headless: true,
    timezoneId: "America/Los_Angeles",
  },
  webServer: [
    {
      command:
        "cd /workspaces/codespaces-blank/BuildAThon-2026/code/backend && export PW_RUN_ID=${PW_RUN_ID:-playwright} && rm -f \"playwright-$PW_RUN_ID.db\" && export DATABASE_URL=sqlite:///./playwright-$PW_RUN_ID.db ENABLE_TEST_SUPPORT_ENDPOINTS=1 TEST_SUPPORT_TOKEN=buildathon-e2e && /workspaces/codespaces-blank/.venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8000",
      url: "http://127.0.0.1:8000/health",
      timeout: 60_000,
      reuseExistingServer: false,
    },
    {
      command:
        "cd /workspaces/codespaces-blank/BuildAThon-2026/code/frontend && npm run dev -- --host 127.0.0.1 --port 5173",
      url: "http://127.0.0.1:5173",
      timeout: 60_000,
      reuseExistingServer: false,
    },
  ],
});
