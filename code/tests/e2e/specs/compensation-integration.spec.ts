import { expect, test } from "@playwright/test";

import { resetDemoState } from "./support";

test.beforeEach(async ({ request }) => {
  await resetDemoState(request);
});

test("Compensation and integration: PTO, comp-time, and payroll payload are surfaced in the browser", async ({ page }) => {
  await page.goto("/");

  const compensationCard = page.locator("section.card").filter({ has: page.getByRole("heading", { name: "Compensation & Integration" }) });
  const ptoCard = page.getByRole("article", { name: "PTO balance and adjustments" });
  const compTimeCard = page.getByRole("article", { name: "Comp-time balance and adjustments" });
  const payloadCard = page.getByRole("article", { name: "Payroll integration payload" });

  await expect(compensationCard.getByRole("heading", { name: "Compensation & Integration" })).toBeVisible();
  await expect(ptoCard).toContainText("Total Days");
  await expect(ptoCard).toContainText("20");
  await expect(compTimeCard).toContainText("Total Comp Time");
  await expect(compTimeCard).toContainText("0 min");
  await expect(payloadCard).toContainText("Schema Version");
  await expect(payloadCard).toContainText("1.0");
  await expect(payloadCard).toContainText("future-payroll-integration");
  await expect(payloadCard).toContainText("E001");

  await ptoCard.getByLabel("PTO adjustment days").fill("2");
  await ptoCard.getByRole("button", { name: "Adjust PTO Balance" }).click();
  await expect(page.getByRole("status")).toContainText("PTO adjusted by 2 day(s)");
  await expect(ptoCard).toContainText("22");

  await compTimeCard.getByLabel("Comp-time adjustment minutes").fill("30");
  await compTimeCard.getByLabel("Adjustment reason").fill("Manual correction");
  await compTimeCard.getByRole("button", { name: "Adjust Comp Time" }).click();
  await expect(page.getByRole("status")).toContainText("Comp-time adjusted by 30 minute(s)");
  await expect(compTimeCard).toContainText("30 min");
});