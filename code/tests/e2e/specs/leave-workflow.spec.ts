import { expect, test, type Page } from "@playwright/test";

async function submitLeave(page: Page, startDate: string, endDate: string) {
  await page.getByLabel("Leave start date").fill(startDate);
  await page.getByLabel("Leave end date").fill(endDate);
  await page.getByRole("button", { name: "Submit Leave Request" }).click();
}

test("Leave workflow: employee submits request and manager approval updates balance", async ({ page }) => {
  await page.goto("/");

  await submitLeave(page, "2026-05-20", "2026-05-21");
  await expect(page.locator("p.message")).toContainText("Leave request created");

  const leaveCard = page.locator("section.card").filter({ has: page.getByRole("heading", { name: "Leave Workflow" }) });
  await expect(leaveCard.getByText("PENDING", { exact: true }).first()).toBeVisible();
  await expect(leaveCard.locator("li").filter({ hasText: "2026-05-20 to 2026-05-21" }).first()).toBeVisible();

  await leaveCard.getByRole("button", { name: "Approve Leave Request" }).first().click();
  await expect(page.locator("p.message")).toContainText("Leave request approved");
  await expect(leaveCard.getByText("APPROVED", { exact: true }).first()).toBeVisible();
  await expect(leaveCard.getByText("Used Days")).toBeVisible();
  await expect(leaveCard.getByText("1").first()).toBeVisible();
});