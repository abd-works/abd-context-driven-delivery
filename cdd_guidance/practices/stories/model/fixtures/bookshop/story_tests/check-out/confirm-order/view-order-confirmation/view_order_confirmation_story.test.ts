/**
 * Epic: Check Out
 * Sub-epic: Confirm Order
 * Map: ../../../../.context/story-map.md#s-customer----view-order-confirmation
 * Model: ../../../../.context/domain-model.md
 */

import { expect } from "vitest";
import { scenario, story } from "../../../story-test";
import { OrderNotFound, OrderRepository } from "../../../../src/bookshop/order";
import { missingOrderNumber, submittedOrder } from "../examples/order.examples";

/**
 * Story: View Order Confirmation
 * Actor: Customer
 */
story("View Order Confirmation", () => {
  const orders = new OrderRepository();

  scenario("Show the confirmation of a submitted order", ({ given, when, then }) => {
    let confirmation: ReturnType<typeof submittedOrder.confirmation>;
    given("the Bookshop keeps [Order](../../../../.context/domain-model.md#order-aggregate-root-entity) submittedOrder", () => {
      orders.create(submittedOrder);
    });
    when("the Customer views the confirmation of order 1001", () => {
      // Order.confirmation()
      confirmation = orders.load(submittedOrder.orderNumber).confirmation();
    });
    then("the Customer sees order 1001 with total 5", () => {
      expect(confirmation.orderNumber).toBe("1001");
      expect(confirmation.total).toBe(5);
    }).and("the Customer sees status submitted", () => {
      expect(confirmation.status).toBe("submitted");
    });
  });

  scenario("Refuse an order number the Bookshop does not keep", ({ when, then }) => {
    let viewing: () => unknown;
    when("the Customer views the confirmation of order 9999", () => {
      viewing = () => orders.load(missingOrderNumber).confirmation();
    });
    then("the Bookshop refuses with \"order 9999 is not found\"", () => {
      expect(viewing).toThrow(OrderNotFound);
    });
  });
});
