import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./specs",
  timeout: 60_000,
  retries: 0,
  use: {
    baseURL: "http://127.0.0.1:5173",
    trace: "on-first-retry",
    headless: true,
  },
  webServer: [
    {
      command:
        "cd /workspaces/codespaces-blank/BuildAThon-2026/code/backend && /workspaces/codespaces-blank/.venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8000",
      url: "http://127.0.0.1:8000/health",
      timeout: 60_000,
      reuseExistingServer: true,
    },
    {
      command:
        "cd /workspaces/codespaces-blank/BuildAThon-2026/code/frontend && npm run dev -- --host 127.0.0.1 --port 5173",
      url: "http://127.0.0.1:5173",
      timeout: 60_000,
      reuseExistingServer: true,
    },
  ],
});
