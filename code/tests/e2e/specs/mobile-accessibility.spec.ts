import fs from "node:fs";
import path from "node:path";

import { expect, test, type APIRequestContext, type Page, type TestInfo } from "@playwright/test";

const runId = process.env.PW_RUN_ID ?? new Date().toISOString().replace(/[:.]/g, "-");
const archiveDir = path.resolve(__dirname, "../../../../artifacts/playwright-runs", runId);
const authHeader = {
  Authorization: `Bearer ${process.env.PW_DEMO_AUTH_TOKEN ?? "demo-employee-token"}`,
};

async function saveStepScreenshot(page: Page, testInfo: TestInfo, fileName: string) {
  const testOutputPath = testInfo.outputPath(fileName);
  await page.screenshot({ path: testOutputPath, fullPage: true });

  fs.mkdirSync(archiveDir, { recursive: true });
  const archivePath = path.join(archiveDir, fileName);
  fs.copyFileSync(testOutputPath, archivePath);
}

async function ensureNoOpenShift(request: APIRequestContext) {
  const response = await request.post("http://127.0.0.1:8000/employees/E001/clock-out", {
    headers: authHeader,
  });
  if (![200, 409].includes(response.status())) {
    throw new Error(`Unexpected preflight clock-out status: ${response.status()}`);
  }
}

test("Mobile accessibility baseline: responsive controls and status semantics", async ({ page, request }, testInfo) => {
  await ensureNoOpenShift(request);
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");

  await expect(page.getByRole("heading", { name: "Workforce Time Capture Console" })).toBeVisible();
  await saveStepScreenshot(page, testInfo, "mobile-01-home.png");

  const controls = page.getByRole("region", { name: "Punch controls" });
  await expect(controls).toBeVisible();

  const clockIn = page.getByRole("button", { name: "Clock In" });
  await clockIn.click();

  const statusMessage = page.locator('p[role="status"]');
  await expect(statusMessage).toContainText("Clock-in accepted");
  await saveStepScreenshot(page, testInfo, "mobile-02-clock-in.png");

  const clockOut = page.getByRole("button", { name: "Clock Out" });
  await clockOut.click();
  await expect(statusMessage).toContainText("Clock-out accepted");

  await expect(page.getByRole("heading", { name: "Shift History" })).toBeVisible();
  await saveStepScreenshot(page, testInfo, "mobile-03-clock-out.png");
});
