/**
 * # @toolset-manifest python -m tools manifest context_tools.stories.stories:Stories
 * Exploration — Remove Item From Cart main flow (UX examples / manage-customer-orders).
 */

import { ManageCustomerOrdersHelper } from "../../manage-customer-orders-helper.js";
import { assert } from "../../../../story-demo/play-dual-runner/soft-assert.js";
import { scenario, story } from "../../../../story-demo/play-dual-runner/story-test-core.js";

const helper = new ManageCustomerOrdersHelper();

/** @param {"fake"|"isolated"|"production"} mode */
export function createRemoveItemFromCartStory(mode) {
  story("Remove Item From Cart", () => {
    scenario("cart line removed leaving remaining items", ({ given, when, then, expose, input, session }) => {
      let cart;

      given("a Cart with Cart Items for Widget and Gadget", () => {
        // Interactive keeps the live cart; Play/factory only when none yet.
        cart = session("cart", () => helper.givenCartWithThreeItems({ mode }).cart);
      });

      // Play / node default removes Gadget; Interactive selects a cart line first.
      when("the Customer removes a Product from the Cart", () => {
        cart.removeItem(input("product", "Gadget"));
      });

      then("the Cart no longer contains the removed Product", () => {
        const removed = input("product", "Gadget");
        assert.ok(!cart.items.some((i) => i.product === removed));
      });

      then("And the Cart still contains at least one other Cart Item", () => {
        assert.ok(cart.items.length >= 1);
      });

      expose(() => ({
        cart,
        product: { name: input("product", "Gadget") },
        itemCount: cart.items.length,
        total: cart.computeTotal(),
        products: cart.items.map((i) => i.product),
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
    createRemoveItemFromCartStory("fake");
  }
}
