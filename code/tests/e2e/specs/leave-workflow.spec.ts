import { expect, test, type Page } from "@playwright/test";

import { resetDemoState } from "./support";

const leaveStartDate = "2026-06-03";
const leaveEndDate = "2026-06-04";

async function submitLeave(page: Page, startDate: string, endDate: string) {
  await page.getByLabel("Leave start date").fill(startDate);
  await page.getByLabel("Leave end date").fill(endDate);
  await page.getByRole("button", { name: "Submit Leave Request" }).click();
}

test.beforeEach(async ({ request }) => {
  await resetDemoState(request);
});

test("Leave workflow: employee submits request and manager approval updates balance", async ({ page }) => {
  await page.goto("/");

  await submitLeave(page, leaveStartDate, leaveEndDate);
  await expect(page.locator("p.message")).toContainText("Leave request created");

  const leaveCard = page.locator("section.card").filter({ has: page.getByRole("heading", { name: "Leave Workflow" }) });
  const requestRow = leaveCard.locator("li").filter({ hasText: `${leaveStartDate} to ${leaveEndDate}` });
  await expect(requestRow).toHaveCount(1);
  await expect(requestRow.first()).toContainText("PENDING");

  await requestRow.getByRole("button", { name: "Approve Leave Request" }).click();
  await expect(page.locator("p.message")).toContainText("Leave request approved");
  await expect(requestRow).toContainText("APPROVED");
  await expect(requestRow).not.toContainText("Approve Leave Request");
  await expect(leaveCard.locator(".leave-summary dd").nth(1)).toHaveText("2");
  await expect(leaveCard.locator(".leave-summary dd").nth(2)).toHaveText("18");
});