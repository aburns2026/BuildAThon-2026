import { expect, test } from "@playwright/test";

test("MVP flow: clock in, duplicate validation, clock out, and summary visibility", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { name: "Workforce Time Capture Console" })).toBeVisible();

  await page.getByRole("button", { name: "Clock In" }).click();
  await expect(page.getByText("Clock-in accepted", { exact: false })).toBeVisible();

  await page.getByRole("button", { name: "Clock In" }).click();
  await expect(page.getByText("Duplicate clock-in", { exact: false })).toBeVisible();

  await page.getByRole("button", { name: "Clock Out" }).click();
  await expect(page.getByText("Clock-out accepted", { exact: false })).toBeVisible();

  await expect(page.getByRole("heading", { name: "Shift History" })).toBeVisible();
  await expect(page.getByText("CLOSED", { exact: false })).toBeVisible();

  await expect(page.getByRole("heading", { name: "Payroll Summary" })).toBeVisible();
  await expect(page.getByText("Closed Shifts", { exact: false })).toBeVisible();

  await expect(page.getByRole("heading", { name: "Audit Events" })).toBeVisible();
  await expect(page.getByText("CLOCK_OUT_ACCEPTED", { exact: false })).toBeVisible();
});
