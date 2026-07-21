/**
 * # @toolset-manifest python -m tools manifest contexts.stories.stories:Stories
 * Exploration — Select Product main flow (UX examples / manage-customer-orders).
 */

import { ManageCustomerOrdersHelper } from "../../manage-customer-orders-helper.js";
import { assert } from "../../../../story-demo/play-dual-runner/soft-assert.js";
import { scenario, story } from "../../../../story-demo/play-dual-runner/story-test-core.js";

const helper = new ManageCustomerOrdersHelper();

/** @param {"fake"|"isolated"|"production"} mode */
export function createSelectProductStory(mode) {
  story("Select Product", () => {
    scenario("product selected from catalog for cart", ({ given, when, then, expose, input, session }) => {
      let catalog;
      let selected;

      given("a Product Catalog listing Widgets under Category Hardware", () => {
        catalog = session("catalog", () => helper.givenHardwareCatalog({ mode }).catalog);
      });

      given('And a Product "Widget" priced at 49.99 USD', () => {
        assert.ok(catalog.products.some((p) => p.name === "Widget"));
      });

      // Play / node default product is Widget; Interactive sets input from catalog row.
      when("the Customer selects a Product from the Product Catalog", () => {
        const name = input("product", "Widget");
        selected = catalog.products.find((p) => p.name === name);
      });

      then("Product Detail for the selected Product is shown with its unit price", () => {
        const name = input("product", "Widget");
        const listed = catalog.products.find((p) => p.name === name);
        assert.ok(selected);
        assert.equal(selected?.name, name);
        assert.equal(selected?.unitPrice, listed?.unitPrice);
      });

      then("And the Product is ready to add to the Cart", () => {
        assert.equal(selected?.name, input("product", "Widget"));
      });

      expose(() => ({
        catalog,
        product: selected,
        productName: selected?.name ?? null,
        unitPrice: selected?.unitPrice ?? null,
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
    createSelectProductStory("fake");
  }
}
