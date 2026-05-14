import fs from "node:fs";
import path from "node:path";

import { expect, test, type APIRequestContext, type Page, type TestInfo } from "@playwright/test";

const runId = process.env.PW_RUN_ID ?? new Date().toISOString().replace(/[:.]/g, "-");
const archiveDir = path.resolve(
  __dirname,
  "../../../../artifacts/playwright-runs",
  runId
);
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

test("MVP flow: clock in, duplicate validation, clock out, and summary visibility", async ({ page, request }, testInfo) => {
  await ensureNoOpenShift(request);
  await page.goto("/");
  await saveStepScreenshot(page, testInfo, "01-home.png");

  await expect(page.getByRole("heading", { name: "Workforce Time Capture Console" })).toBeVisible();

  await page.getByRole("button", { name: "Clock In" }).click();
  await expect(page.locator("p.message")).toContainText("Clock-in accepted");
  await saveStepScreenshot(page, testInfo, "02-clock-in.png");

  await page.getByRole("button", { name: "Clock In" }).click();
  await expect(page.locator("p.message")).toContainText("Duplicate clock-in");
  await saveStepScreenshot(page, testInfo, "03-duplicate-validation.png");

  await page.getByRole("button", { name: "Clock Out" }).click();
  await expect(page.locator("p.message")).toContainText("Clock-out accepted");
  await saveStepScreenshot(page, testInfo, "04-clock-out.png");

  const shiftHistoryCard = page.locator("article.card").filter({ has: page.getByRole("heading", { name: "Shift History" }) });
  await expect(shiftHistoryCard.getByRole("heading", { name: "Shift History" })).toBeVisible();
  await expect(shiftHistoryCard.getByText("CLOSED", { exact: true }).first()).toBeVisible();

  const summaryCard = page.locator("article.card").filter({ has: page.getByRole("heading", { name: "Payroll Summary" }) });
  await expect(summaryCard.getByRole("heading", { name: "Payroll Summary" })).toBeVisible();
  await expect(summaryCard.getByText("Closed Shifts", { exact: false })).toBeVisible();

  const breakdownCard = page.locator("article.card").filter({ has: page.getByRole("heading", { name: "Payroll Breakdown" }) });
  await expect(breakdownCard.getByRole("heading", { name: "Payroll Breakdown" })).toBeVisible();
  await expect(breakdownCard.getByText("Regular Minutes", { exact: false })).toBeVisible();

  const complianceCard = page.locator("article.card").filter({ has: page.getByRole("heading", { name: "Compliance Report" }) });
  await expect(complianceCard.getByRole("heading", { name: "Compliance Report" })).toBeVisible();
  await expect(complianceCard.getByText("Tax Validation Status", { exact: false })).toBeVisible();
  await expect(complianceCard.getByText("PASS", { exact: true }).first()).toBeVisible();

  const auditCard = page.locator("section.card").filter({ has: page.getByRole("heading", { name: "Audit Events" }) });
  await expect(auditCard.getByRole("heading", { name: "Audit Events" })).toBeVisible();
  await expect(auditCard.getByText("CLOCK_OUT_ACCEPTED", { exact: false }).first()).toBeVisible();
  await saveStepScreenshot(page, testInfo, "05-final-state.png");
});
