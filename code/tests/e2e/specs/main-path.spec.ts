import fs from "node:fs";
import path from "node:path";

import { expect, test, type Page, type TestInfo } from "@playwright/test";

import { resetDemoState } from "./support";

const runId = process.env.PW_RUN_ID ?? new Date().toISOString().replace(/[:.]/g, "-");
const archiveDir = path.resolve(
  __dirname,
  "../../../../artifacts/playwright-runs",
  runId
);
async function saveStepScreenshot(page: Page, testInfo: TestInfo, fileName: string) {
  const testOutputPath = testInfo.outputPath(fileName);
  await page.screenshot({ path: testOutputPath, fullPage: true });

  fs.mkdirSync(archiveDir, { recursive: true });
  const archivePath = path.join(archiveDir, fileName);
  fs.copyFileSync(testOutputPath, archivePath);
}

test.beforeEach(async ({ request }) => {
  await resetDemoState(request);
});

test("MVP flow: clock in, duplicate validation, clock out, and summary visibility", async ({ page }, testInfo) => {
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
  const shiftRows = shiftHistoryCard.locator("li");
  await expect(shiftRows).toHaveCount(1);
  await expect(shiftRows.first()).toContainText("CLOSED");

  const summaryCard = page.locator("article.card").filter({ has: page.getByRole("heading", { name: "Payroll Summary" }) });
  await expect(summaryCard.getByRole("heading", { name: "Payroll Summary" })).toBeVisible();
  await expect(summaryCard.locator("dd").nth(1)).toHaveText("1");

  const breakdownCard = page.locator("article.card").filter({ has: page.getByRole("heading", { name: "Payroll Breakdown" }) });
  await expect(breakdownCard.getByRole("heading", { name: "Payroll Breakdown" })).toBeVisible();
  await expect(breakdownCard.getByText("Regular Minutes", { exact: false })).toBeVisible();

  const complianceCard = page.locator("article.card").filter({ has: page.getByRole("heading", { name: "Compliance Report" }) });
  await expect(complianceCard.getByRole("heading", { name: "Compliance Report" })).toBeVisible();
  await expect(complianceCard.getByText("EMPLOYEE ORG ASSIGNMENT PRESENT", { exact: false })).toBeVisible();
  await expect(complianceCard.getByText("NO OPEN SHIFT PENDING", { exact: false })).toBeVisible();
  await expect(complianceCard.locator(".status-pill.pass").first()).toBeVisible();

  const auditCard = page.locator("section.card").filter({ has: page.getByRole("heading", { name: "Audit Events" }) });
  await expect(auditCard.getByRole("heading", { name: "Audit Events" })).toBeVisible();
  const auditRows = auditCard.locator("li");
  await expect(auditRows).toHaveCount(3);
  await expect(auditRows.nth(0)).toContainText("CLOCK_OUT_ACCEPTED");
  await expect(auditRows.nth(1)).toContainText("CLOCK_IN_REJECTED");
  await expect(auditRows.nth(2)).toContainText("CLOCK_IN_ACCEPTED");
  await saveStepScreenshot(page, testInfo, "05-final-state.png");
});
