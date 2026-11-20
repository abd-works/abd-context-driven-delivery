/** Confirm Order in the browser: what the Customer sees on the confirmation page. */

import { expect, test } from "@playwright/test";

test.describe("View Order Confirmation", () => {
  test("Show the confirmation of a submitted order", async ({ page }) => {
    await seedOrder(page, "1001", 5);
    await page.goto("/orders/1001/confirmation");
    await expect(page.getByRole("heading", { name: "Order 1001" })).toBeVisible();
    await expect(page.getByText("Total 5")).toBeVisible();
  });
});

test.describe("Cancel Order", () => {
  test("Cancel a submitted order", async ({ page }) => {
    await seedOrder(page, "1001", 5);
    await page.goto("/orders/1001/confirmation");
    await page.getByRole("button", { name: "Cancel order" }).click();
    await expect(page.getByText("Status cancelled")).toBeVisible();
  });
});

async function seedOrder(page: import("@playwright/test").Page, orderNumber: string, total: number): Promise<void> {
  await page.request.post("/test/orders", { data: { orderNumber, total } });
}
