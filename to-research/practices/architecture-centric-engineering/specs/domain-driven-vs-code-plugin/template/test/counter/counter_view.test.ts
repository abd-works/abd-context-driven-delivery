// test/counter/counter_view.test.ts
import { describe, expect, beforeEach } from "vitest";
import * as path from "path";
import { CounterView } from "../../src/counter/view/counter_view.js";
import { Counter } from "../../src/counter/counter.js";
import { CounterTest } from "./counter_test.js";
import type { ICounter } from "../../src/counter/counter.js";
import { Uri, createMockWebviewPanel } from "../__mocks__/vscode.js";
import type { WebviewPanel } from "../__mocks__/vscode.js";

describe("CounterView", () => {
  let posted: unknown[];
  let mockPanel: WebviewPanel;
  // Point to project root so getHtml() can find templates
  const extensionUri = Uri.file(path.resolve(__dirname, "../.."));

  beforeEach(() => {
    posted = [];
    mockPanel = createMockWebviewPanel(posted);
  });

  class CounterViewTest extends CounterTest {
    private _view?: CounterView;

    protected createCounter(): ICounter {
      const counter = new Counter();
      this._view = new CounterView(
        mockPanel as unknown as import("vscode").WebviewPanel,
        counter,
        extensionUri as unknown as import("vscode").Uri
      );
      return this._view;
    }

    protected override assertTotal(counter: ICounter, expected: number): void {
      // First: standard domain assertion
      super.assertTotal(counter, expected);

      // Server view adds: verify postMessage was called with total
      // (only when there are messages - "starts at zero" has no operations)
      if (posted.length > 0) {
        expect(posted).toContainEqual({ total: expected });
      }

      // Verify the actual getHtml() renders the expected total
      const html = this._view!.getHtml();
      expect(html).toContain(`<span id="total">${expected}</span>`);
    }
  }

  new CounterViewTest().registerTests();
});
