import { expect, test } from "@playwright/test";

import { resetDemoState } from "./support";

test.beforeEach(async ({ request }) => {
  await resetDemoState(request);
});

test("Scheduling validation: invalid schedule shows error and valid retry replaces stale UI state", async ({ page }) => {
  await page.goto("/");
  const schedulingCard = page.locator("section.card").filter({ has: page.getByRole("heading", { name: "Scheduling Workflow" }) });

  await schedulingCard.getByLabel("Scheduled start").fill("2026-05-23T11:00");
  await schedulingCard.getByLabel("Scheduled end").fill("2026-05-23T14:00");
  await schedulingCard.getByLabel("Break minutes").fill("30");
  await schedulingCard.getByRole("button", { name: "Schedule Shift" }).click();

  const message = page.locator("p.message");
  await expect(message).toContainText("scheduled shift must cover configured core hours");
  await expect(page.locator(".schedule-list li")).toHaveCount(0);

  await schedulingCard.getByLabel("Scheduled start").fill("2026-05-23T09:00");
  await schedulingCard.getByLabel("Scheduled end").fill("2026-05-23T17:00");
  await schedulingCard.getByLabel("Break minutes").fill("30");
  await schedulingCard.getByRole("button", { name: "Schedule Shift" }).click();

  await expect(message).toContainText("Scheduled shift created");
  await expect(message).not.toContainText("configured core hours");
  await expect(page.locator(".schedule-list li")).toHaveCount(1);
});

test("Leave approval: duplicate approval is rejected after the first approval succeeds", async ({ page, request }) => {
  await page.goto("/");

  await page.getByRole("button", { name: "Submit Leave Request" }).click();
  const leaveCard = page.locator("section.card").filter({ has: page.getByRole("heading", { name: "Leave Workflow" }) });
  const requestRow = leaveCard.locator("li").first();
  await expect(requestRow).toContainText("PENDING");

  await requestRow.getByRole("button", { name: "Approve Leave Request" }).click();
  await expect(requestRow).toContainText("APPROVED");

  const leaveRequestId = await requestRow.evaluate((node) => node.getAttribute("data-leave-request-id"));
  expect(leaveRequestId).not.toBeNull();

  const duplicateApproval = await request.post(`http://127.0.0.1:8000/leave-requests/${leaveRequestId}/approve`, {
    headers: {
      Authorization: "Bearer demo-manager-token",
      "x-role": "MANAGER",
    },
  });

  expect(duplicateApproval.status()).toBe(409);
  await expect(page.locator("p.message")).toContainText("Leave request approved");
});

test("Clock-in auth failure: backend detail is shown to the user", async ({ page }) => {
  await page.goto("/");
  await page.evaluate(() => {
    window.localStorage.setItem("buildathon.demoAuthToken", "not-a-real-token");
  });
  await page.getByRole("button", { name: "Clock In" }).click();
  await expect(page.locator("p.message")).toContainText("Invalid bearer token");
});

test("Leave validation: reversed leave dates show the backend validation message", async ({ page }) => {
  await page.goto("/");

  const leaveCard = page.locator("section.card").filter({ has: page.getByRole("heading", { name: "Leave Workflow" }) });
  await leaveCard.getByLabel("Leave start date").fill("2026-05-21");
  await leaveCard.getByLabel("Leave end date").fill("2026-05-20");
  await leaveCard.getByRole("button", { name: "Submit Leave Request" }).click();

  await expect(page.locator("p.message")).toContainText("end_date must be on or after start_date");
  await expect(leaveCard.locator("li")).toHaveCount(0);
});

test("Leave approval auth failure: real backend role mismatch is shown to the user", async ({ page }) => {
  await page.addInitScript(() => {
    window.localStorage.setItem("buildathon.managerAuthToken", "demo-employee-token");
  });

  await page.goto("/");
  await page.getByRole("button", { name: "Submit Leave Request" }).click();

  const leaveCard = page.locator("section.card").filter({ has: page.getByRole("heading", { name: "Leave Workflow" }) });
  const requestRow = leaveCard.locator("li").first();
  await expect(requestRow).toContainText("PENDING");

  await requestRow.getByRole("button", { name: "Approve Leave Request" }).click();

  await expect(page.locator("p.message")).toContainText("x-role does not match authenticated principal");
  await expect(requestRow).toContainText("PENDING");
});

test("Policy save auth failure: real backend admin role mismatch is shown to the user", async ({ page }) => {
  await page.goto("/");

  const adminCard = page.locator("section.card").filter({ has: page.getByRole("heading", { name: "Enterprise Admin Overview" }) });
  const policyCard = adminCard.getByLabel("Policy controls");
  const schedulingCard = page.locator("section.card").filter({ has: page.getByRole("heading", { name: "Scheduling Workflow" }) });

  await expect(schedulingCard).toContainText("30 min");
  await expect(schedulingCard).toContainText("10:00 - 15:00");

  await policyCard.getByLabel("Minimum break minutes").fill("45");
  await policyCard.getByLabel("Core hour start").fill("9");
  await policyCard.getByLabel("Core hour end").fill("16");

  await page.evaluate(() => {
    window.localStorage.setItem("buildathon.adminAuthToken", "demo-employee-token");
  });

  await policyCard.getByRole("button", { name: "Save Policy Settings" }).click();

  await expect(page.locator("p.message")).toContainText("x-role does not match authenticated principal");
  await expect(schedulingCard).toContainText("30 min");
  await expect(schedulingCard).toContainText("10:00 - 15:00");
  await expect(policyCard.getByLabel("Minimum break minutes")).toHaveValue("30");
  await expect(policyCard.getByLabel("Core hour start")).toHaveValue("10");
  await expect(policyCard.getByLabel("Core hour end")).toHaveValue("15");
});

test("Compensation validation: invalid PTO and comp-time adjustments show backend validation details", async ({ page }) => {
  await page.goto("/");

  const compensationCard = page.locator("section.card").filter({ has: page.getByRole("heading", { name: "Compensation & Integration" }) });
  const ptoCard = compensationCard.getByLabel("PTO balance and adjustments");
  const compTimeCard = compensationCard.getByLabel("Comp-time balance and adjustments");
  const message = page.locator("p.message");

  await ptoCard.getByLabel("PTO adjustment days").fill("0");
  await ptoCard.getByRole("button", { name: "Adjust PTO Balance" }).click();
  await expect(message).toContainText("days_delta cannot be 0");

  await compTimeCard.getByLabel("Comp-time adjustment minutes").fill("15");
  await compTimeCard.getByLabel("Adjustment reason").fill("");
  await compTimeCard.getByRole("button", { name: "Adjust Comp Time" }).click();
  await expect(message).toContainText("reason is required");
  await expect(compTimeCard).toContainText("0 min");
});

test("Initial load failure: UI shell still renders with fallback state", async ({ page }) => {
  await page.route("**/employees/E001/*", async (route) => {
    if (route.request().method() === "GET") {
      await route.fulfill({
        status: 500,
        contentType: "application/json",
        body: JSON.stringify({ detail: "Synthetic load failure" }),
      });
      return;
    }
    await route.continue();
  });
  await page.route("**/policies", async (route) => {
    if (route.request().method() === "GET") {
      await route.fulfill({
        status: 500,
        contentType: "application/json",
        body: JSON.stringify({ detail: "Synthetic load failure" }),
      });
      return;
    }
    await route.continue();
  });

  await page.goto("/");

  await expect(page.getByRole("heading", { name: "Workforce Time Capture Console" })).toBeVisible();
  await expect(page.getByText("No shifts yet.", { exact: false })).toBeVisible();
  await expect(page.getByText("Policy guidance unavailable.", { exact: false })).toBeVisible();
});