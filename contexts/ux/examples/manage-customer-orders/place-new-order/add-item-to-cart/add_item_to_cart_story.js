/**
 * # @toolset-manifest python -m tools manifest contexts.stories.stories:Stories
 * Exploration — Add Item To Cart main flow (UX examples / manage-customer-orders).
 */

import { ManageCustomerOrdersHelper } from "../../manage-customer-orders-helper.js";
import { assert } from "../../../../story-demo/play-dual-runner/soft-assert.js";
import { scenario, story } from "../../../../story-demo/play-dual-runner/story-test-core.js";

const helper = new ManageCustomerOrdersHelper();

/** @param {"fake"|"isolated"|"production"} mode */
export function createAddItemToCartStory(mode) {
  story("Add Item To Cart", () => {
    scenario("selected product added to empty cart", ({ given, when, then, expose, input, session }) => {
      let cart;
      let product;

      given("an empty Cart for Customer Alex Morgan", () => {
        cart = session("cart", () => helper.givenEmptyCart({ mode }).cart);
      });

      given('And a selected Product "Widget" at 49.99 USD', () => {
        const prior = session("product", null);
        const name = input("product", null) ?? prior?.name ?? "Widget";
        product = helper.givenSelectedProduct({ mode, name }).product;
      });

      // Play / node defaults: Widget × 2; Interactive sets product + quantity inputs.
      when('the Customer adds Product "Widget" with Quantity 2 to the Cart', () => {
        cart.addItem(product.name, input("quantity", 2), product.unitPrice);
      });

      then("the Cart contains one Cart Item for Widget with Quantity 2", () => {
        const quantity = input("quantity", 2);
        assert.equal(cart.items.length, 1);
        assert.equal(cart.items[0].product, input("product", "Widget"));
        assert.equal(cart.items[0].quantity, quantity);
      });

      then("And the Cart line total for Widget is 99.98 USD", () => {
        const quantity = input("quantity", 2);
        const expected = Math.round(quantity * product.unitPrice * 100) / 100;
        assert.equal(cart.items[0].quantity * cart.items[0].unitPrice, expected);
      });

      expose(() => ({
        cart,
        product,
        quantity: input("quantity", 2),
        itemCount: cart.items.length,
        total: cart.computeTotal(),
      }));
    });
  });
}

if (typeof process !== "undefined" && process.versions?.node) {
  const [{ fileURLToPath }, { default: path }] = await Promise.all([
    import("node:url"),
    import("node:path"),
  ]);
  await import("../../../../story-demo/play-dual-runner/story-test-node.js");
  const thisFile = fileURLToPath(import.meta.url);
  const entry = process.argv[1] && path.resolve(process.argv[1]);
  if (entry && path.resolve(thisFile) === entry) {
    createAddItemToCartStory("fake");
  }
}
