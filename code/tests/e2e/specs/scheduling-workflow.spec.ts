import { expect, test, type Page } from "@playwright/test";

import { resetDemoState } from "./support";

const scheduledStartAt = "2026-05-23T09:15";
const scheduledEndAt = "2026-05-23T17:45";
const scheduledBreakMinutes = "45";

async function toUiDateTime(page: Page, value: string) {
  return page.evaluate((input) => new Date(input).toLocaleString(), value);
}

async function submitScheduledShift(page: Page, startAt: string, endAt: string, breakMinutes: string) {
  const schedulingCard = page.locator("section.card").filter({ has: page.getByRole("heading", { name: "Scheduling Workflow" }) });
  await schedulingCard.getByLabel("Scheduled start").fill(startAt);
  await schedulingCard.getByLabel("Scheduled end").fill(endAt);
  await schedulingCard.getByLabel("Break minutes").fill(breakMinutes);
  await schedulingCard.getByRole("button", { name: "Schedule Shift" }).click();
}

test.beforeEach(async ({ request }) => {
  await resetDemoState(request);
});

test("Scheduling workflow: seeded local times submit successfully in the demo timezone", async ({ page }) => {
  await page.goto("/");

  const schedulingCard = page.locator("section.card").filter({ has: page.getByRole("heading", { name: "Scheduling Workflow" }) });
  await expect(schedulingCard.getByLabel("Scheduled start")).toHaveValue("2026-05-22T09:00");
  await expect(schedulingCard.getByLabel("Scheduled end")).toHaveValue("2026-05-22T17:00");

  await schedulingCard.getByRole("button", { name: "Schedule Shift" }).click();
  await expect(page.locator("p.message")).toContainText("Scheduled shift created");

  const expectedStart = await toUiDateTime(page, "2026-05-22T09:00");
  const expectedEnd = await toUiDateTime(page, "2026-05-22T17:00");
  const scheduledRow = schedulingCard
    .locator("li")
    .filter({ hasText: expectedStart })
    .filter({ hasText: expectedEnd });

  await expect(scheduledRow).toHaveCount(1);
  await expect(scheduledRow).toContainText("Break compliant");
});

test("Scheduling workflow: manager can create and view a scheduled shift", async ({ page }) => {
  await page.goto("/");

  const schedulingCard = page.locator("section.card").filter({ has: page.getByRole("heading", { name: "Scheduling Workflow" }) });
  await expect(schedulingCard.getByText("Minimum Break", { exact: true })).toBeVisible();
  await expect(schedulingCard.getByText("Core Hours", { exact: true })).toBeVisible();

  await submitScheduledShift(page, scheduledStartAt, scheduledEndAt, scheduledBreakMinutes);
  await expect(page.locator("p.message")).toContainText("Scheduled shift created");

  const expectedStart = await toUiDateTime(page, scheduledStartAt);
  const expectedEnd = await toUiDateTime(page, scheduledEndAt);

  const scheduledRow = schedulingCard
    .locator("li")
    .filter({ hasText: expectedStart })
    .filter({ hasText: expectedEnd });
  await expect(scheduledRow).toHaveCount(1);
  await expect(scheduledRow).toContainText("SCHEDULED");
  await expect(scheduledRow).toContainText(`Break ${scheduledBreakMinutes} min`);
  await expect(scheduledRow).toContainText("Break compliant");
});