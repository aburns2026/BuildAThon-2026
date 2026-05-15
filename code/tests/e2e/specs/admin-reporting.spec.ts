import { expect, test } from "@playwright/test";

import { resetDemoState } from "./support";

test.beforeEach(async ({ request }) => {
  await resetDemoState(request);
});

test("Enterprise admin and reporting views surface company, report, and export data", async ({ page }) => {
  await page.goto("/");

  const adminCard = page.locator("section.card").filter({ has: page.getByRole("heading", { name: "Enterprise Admin Overview" }) });
  const reportingCard = page.locator("section.card").filter({ has: page.getByRole("heading", { name: "Operational Reporting" }) });
  const schedulingCard = page.locator("section.card").filter({ has: page.getByRole("heading", { name: "Scheduling Workflow" }) });
  const policyCard = adminCard.getByLabel("Policy controls");
  const locationCard = adminCard.getByLabel("Location assignment workflow");
  const notificationCard = adminCard.getByLabel("Notification stub settings");
  const secretCard = adminCard.getByLabel("Secret provider settings");
  const payrollExportCard = reportingCard.getByLabel("Payroll export status", { exact: true });
  const locationPayrollExportCard = reportingCard.getByLabel("Location payroll export status", { exact: true });

  await expect(adminCard.getByRole("heading", { name: "Enterprise Admin Overview" })).toBeVisible();
  await expect(adminCard.getByText("Company COMP-001")).toBeVisible();
  await expect(adminCard.getByText("Company Directory")).toBeVisible();
  await expect(adminCard.locator("li").first()).toContainText("E001");
  await expect(adminCard.locator("li").first()).toContainText("LOC-001");
  await expect(adminCard.getByText("Location Coverage")).toBeVisible();
  await expect(adminCard.getByText("Assigned employees")).toBeVisible();

  await expect(reportingCard.getByRole("heading", { name: "Operational Reporting" })).toBeVisible();
  await expect(reportingCard.getByText("Operational Summary")).toBeVisible();
  await expect(reportingCard.getByText("Accepted Events")).toBeVisible();
  await expect(reportingCard.getByText("CrossCheck Summary")).toBeVisible();
  await expect(reportingCard.getByText("MATCH")).toBeVisible();
  await expect(reportingCard.getByText("Payroll Export Readiness")).toBeVisible();
  await expect(payrollExportCard.locator("dd").nth(0)).toHaveText("READY");
  await expect(payrollExportCard.locator("dd").nth(1)).toHaveText("1");
  await expect(reportingCard.getByText("Location Payroll Export")).toBeVisible();
  await expect(locationPayrollExportCard.locator("dd").nth(0)).toHaveText("READY");
  await expect(locationPayrollExportCard.locator("dd").nth(1)).toHaveText("LOC-001");

  await policyCard.getByLabel("Minimum break minutes").fill("45");
  await policyCard.getByLabel("Core hour start").fill("9");
  await policyCard.getByLabel("Core hour end").fill("16");
  await policyCard.getByRole("button", { name: "Save Policy Settings" }).click();
  await expect(page.getByRole("status")).toContainText("Policy updated: 45 min minimum break");
  await expect(schedulingCard).toContainText("45 min");
  await expect(schedulingCard).toContainText("9:00 - 16:00");

  await locationCard.getByLabel("Assigned location").fill("LOC-002");
  await locationCard.getByRole("button", { name: "Save Location Assignment" }).click();
  await expect(page.getByRole("status")).toContainText("Employee E001 moved to LOC-002");
  await expect(adminCard.locator("li").first()).toContainText("LOC-002");
  await expect(locationPayrollExportCard.getByLabel("Location")).toHaveValue("LOC-002");
  await expect(locationPayrollExportCard.locator("dd").nth(1)).toHaveText("LOC-002");

  await notificationCard.getByLabel("Target").fill("https://example.invalid/buildathon-webhook");
  await notificationCard.getByLabel("Secret reference").fill("ops/buildathon/webhook-token");
  await notificationCard.getByLabel("Enable downstream notification stub").check();
  await notificationCard.getByRole("button", { name: "Save Notification Stub" }).click();
  await expect(page.getByRole("status")).toContainText("Notification stub saved for WEBHOOK");
  await expect(notificationCard.getByText(/Status CONFIGURED/i)).toBeVisible();

  await notificationCard.getByRole("button", { name: "Run Notification Test" }).click();
  await expect(page.getByRole("status")).toContainText("Notification test simulated for https://example.invalid/buildathon-webhook");
  await expect(notificationCard.getByText(/TEST_DELIVERY_SIMULATED/i)).toBeVisible();

  await secretCard.getByRole("combobox").selectOption("VAULT_STUB");
  await secretCard.getByLabel("Reference name").fill("kv/buildathon/payroll");
  await secretCard.getByLabel("Enable secret-provider stub").check();
  await secretCard.getByRole("button", { name: "Save Secret Provider" }).click();
  await expect(page.getByRole("status")).toContainText("Secret provider set to VAULT_STUB");
  await expect(secretCard.getByText(/Raw secret values are never stored/i)).toBeVisible();
});