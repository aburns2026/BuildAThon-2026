import { expect, test } from "@playwright/test";

import { resetDemoState } from "./support";

test.beforeEach(async ({ request }) => {
  await resetDemoState(request);
});

test("Accessibility pack: landmarks and names are present", async ({ page }) => {
  await page.goto("/");
  const schedulingCard = page.locator("section.card").filter({ has: page.getByRole("heading", { name: "Scheduling Workflow" }) });

  await expect(page.getByRole("main", { name: "Workforce Time Capture Console" })).toBeVisible();
  await expect(page.getByRole("heading", { level: 1, name: "Workforce Time Capture Console" })).toBeVisible();
  await expect(page.getByRole("region", { name: "Punch controls" })).toBeVisible();

  await expect(page.getByRole("button", { name: "Clock in employee E001" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Clock out employee E001" })).toBeVisible();
  await expect(page.getByLabel("Leave start date")).toBeVisible();
  await expect(page.getByLabel("Leave end date")).toBeVisible();
  await expect(page.getByRole("button", { name: "Submit Leave Request" })).toBeVisible();
  await expect(schedulingCard.getByLabel("Scheduled start")).toBeVisible();
  await expect(schedulingCard.getByLabel("Scheduled end")).toBeVisible();
  await expect(schedulingCard.getByLabel("Break minutes")).toBeVisible();
  await expect(schedulingCard.getByRole("button", { name: "Schedule Shift" })).toBeVisible();

  const status = page.locator("p.message");
  await expect(status).toHaveAttribute("role", "status");
  await expect(status).toHaveAttribute("aria-live", "polite");
});

test("Accessibility pack: keyboard-only punch interaction", async ({ page }) => {
  await page.goto("/");

  const clockIn = page.getByRole("button", { name: "Clock in employee E001" });
  await clockIn.focus();
  await page.keyboard.press("Enter");
  await expect(page.locator("p.message")).toContainText("Clock-in accepted");

  const clockOut = page.getByRole("button", { name: "Clock out employee E001" });
  await expect(clockOut).toBeEnabled();
  await clockOut.focus();
  await expect(clockOut).toBeFocused();
  await clockOut.press("Space");
  await expect(page.locator("p.message")).toContainText("Clock-out accepted");
});

test("Accessibility pack: skip link and headings remain usable", async ({ page }) => {
  await page.goto("/");

  await page.keyboard.press("Tab");
  const skipLink = page.getByRole("link", { name: "Skip to content" });
  await expect(skipLink).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(skipLink).toHaveAttribute("href", "#main-content");

  await expect(page.getByRole("heading", { level: 2, name: "Shift History" })).toBeVisible();
  await expect(page.getByRole("heading", { level: 2, name: "Payroll Summary" })).toBeVisible();
  await expect(page.getByRole("heading", { level: 2, name: "Payroll Breakdown" })).toBeVisible();
  await expect(page.getByRole("heading", { level: 2, name: "Compliance Report" })).toBeVisible();
  await expect(page.getByRole("heading", { level: 2, name: "Leave Workflow" })).toBeVisible();
  await expect(page.getByRole("heading", { level: 2, name: "Scheduling Workflow" })).toBeVisible();
  await expect(page.getByRole("heading", { level: 2, name: "Audit Events" })).toBeVisible();
  await expect(page.getByRole("heading", { level: 2, name: "Missing Punch Exceptions" })).toBeVisible();
});
