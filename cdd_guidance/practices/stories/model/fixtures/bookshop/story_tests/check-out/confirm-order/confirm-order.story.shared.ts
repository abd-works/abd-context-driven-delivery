/**
 * Confirm Order: the shared scenarios the TypeScript tiers replay.
 * Map: .context/story-map.md#e-confirm-order. Model: .context/domain-model.md.
 */

import { expect } from "vitest";
import { scenario, story } from "../../story-test";
import { OrderRepository } from "../../../src/bookshop/order";
import { submittedOrder } from "./examples/order.examples";

export function confirmOrderStories(orders: OrderRepository): void {
  story("Cancel Order", () => {
    scenario("Cancel a submitted order", ({ given, when, then }) => {
      given("the Bookshop keeps Order submittedOrder", () => {
        orders.create(submittedOrder);
      });
      when("the Customer cancels order 1001", () => {
        orders.load(submittedOrder.orderNumber).cancel();
      });
      then("the Order submittedOrder has status cancelled", () => {
        expect(orders.load(submittedOrder.orderNumber).status).toBe("cancelled");
      });
    });

    scenario("Keep the total of a cancelled order", ({ given, when, then }) => {
      given("the Bookshop keeps Order submittedOrder", () => {
        orders.create(submittedOrder);
      });
      when("the Customer cancels order 1001", () => {
        orders.load(submittedOrder.orderNumber).cancel();
      });
      then("the Order submittedOrder keeps total 5", () => {
        expect(orders.load(submittedOrder.orderNumber).total).toBe(5);
      });
    });
  });
}
