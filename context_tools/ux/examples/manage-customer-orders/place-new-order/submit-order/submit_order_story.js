/**
 * # @toolset-manifest python -m tools manifest context_tools.stories.stories:Stories
 * # Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
 * # invoke-edit: action satisfy | toolset: context_tools.stories.stories:Stories
 * # invoke-check: action validate | toolset: context_tools.stories.stories:Stories
 *
 * Exploration — Submit Order main flow (UX examples / manage-customer-orders).
 *
 * Run (node): import story-test-node first, then this file as test entry.
 */

import { ManageCustomerOrdersHelper } from "../../manage-customer-orders-helper.js";
import { assert } from "../../../../story-demo/play-dual-runner/soft-assert.js";
import { scenario, story } from "../../../../story-demo/play-dual-runner/story-test-core.js";

const helper = new ManageCustomerOrdersHelper();

/** @param {"fake"|"isolated"|"production"} mode */
export function createSubmitOrderStory(mode) {
  story("Submit Order", () => {
    scenario("order submitted with valid cart and payment", ({
      given,
      when,
      then,
      expose,
      session,
    }) => {
      let cart;
      let paymentMethod;
      let confirmation;

      given("a Cart with three Items totalling 149.98 USD", () => {
        cart = session("cart", () => helper.givenCartWithThreeItems({ mode }).cart);
        paymentMethod = session("paymentMethod", () => ({
          label: "Visa ending 4242",
          status: "authorised",
        }));
        confirmation = null;
      });

      given('And a Payment Method on file "Visa ending 4242"', () => {
        assert.equal(paymentMethod?.status, "authorised");
      });

      when("the Customer confirms and submits the Order", () => {
        assert.equal(paymentMethod.status, "authorised");
        confirmation = cart.checkout();
      });

      then("an Order Confirmation is issued with an Order Number", () => {
        assert.ok(confirmation?.orderNumber);
        assert.equal(confirmation.status, "placed");
      });

      then("And the Cart is emptied", () => {
        assert.equal(cart.items.length, 0);
        assert.equal(cart.checkedOut, true);
      });

      expose(() => ({
        cart,
        paymentMethod,
        confirmation,
        orderNumber: confirmation?.orderNumber ?? null,
        itemCount: cart.items.length,
        total: cart.checkedOut ? 0 : cart.computeTotal(),
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
    createSubmitOrderStory("fake");
  }
}
