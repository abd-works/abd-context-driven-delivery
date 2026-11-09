/**
 * The explorer tree a mockup page carries, read by the story explorer that draws it.
 */

import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { readExplorerTree } from "./screen-tree.js";

function pageCarrying(text) {
  return {
    querySelector(selector) {
      return selector === "#story-explorer-tree" && text !== null ? { textContent: text } : null;
    },
  };
}

describe("the explorer tree a mockup page carries", () => {
  describe("that the UX map wrote", () => {
    it("should give the explorer the nodes it draws", () => {
      const tree = readExplorerTree(pageCarrying('{"nodes":[{"kind":"screen","name":"cart"}],"screenKeys":{}}'));
      assert.deepEqual(tree.nodes, [{ kind: "screen", name: "cart" }]);
    });

    it("should give the explorer the keys that open each screen", () => {
      const tree = readExplorerTree(pageCarrying('{"nodes":[],"screenKeys":{"cart":["epic:Order","screen:Order//cart"]}}'));
      assert.deepEqual(tree.screenKeys.cart, ["epic:Order", "screen:Order//cart"]);
    });
  });

  describe("that is not JSON", () => {
    it("should raise rather than draw an empty explorer", () => {
      assert.throws(() => readExplorerTree(pageCarrying("{not json")), SyntaxError);
    });
  });

  describe("that the page does not carry", () => {
    it("should raise, naming the tree the page lacks", () => {
      assert.throws(() => readExplorerTree(pageCarrying(null)), /story-explorer-tree/);
    });
  });
});
