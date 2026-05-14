import { expect, test, type Page } from "@playwright/test";

async function submitScheduledShift(page: Page, startAt: string, endAt: string, breakMinutes: string) {
  await page.getByLabel("Scheduled start").fill(startAt);
  await page.getByLabel("Scheduled end").fill(endAt);
  await page.getByLabel("Break minutes").fill(breakMinutes);
  await page.getByRole("button", { name: "Schedule Shift" }).click();
}

test("Scheduling workflow: manager can create and view a scheduled shift", async ({ page }) => {
  await page.goto("/");

  const schedulingCard = page.locator("section.card").filter({ has: page.getByRole("heading", { name: "Scheduling Workflow" }) });
  await expect(schedulingCard.getByText("Minimum Break", { exact: true })).toBeVisible();
  await expect(schedulingCard.getByText("Core Hours", { exact: true })).toBeVisible();

  await submitScheduledShift(page, "2026-05-23T09:00", "2026-05-23T17:00", "30");
  await expect(page.locator("p.message")).toContainText("Scheduled shift created");

  const scheduledRow = schedulingCard.locator("li").first();
  await expect(scheduledRow).toBeVisible();
  await expect(scheduledRow.getByText("SCHEDULED", { exact: true })).toBeVisible();
  await expect(scheduledRow.getByText("Break 30 min", { exact: false })).toBeVisible();
  await expect(scheduledRow.getByText("Break compliant", { exact: false })).toBeVisible();
});