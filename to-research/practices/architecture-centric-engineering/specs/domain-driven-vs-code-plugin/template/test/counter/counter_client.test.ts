// test/counter/counter_client.test.ts
import { describe, expect, beforeEach, vi } from "vitest";
import { readFileSync } from "fs";
import { resolve } from "path";
import { JSDOM } from "jsdom";
import { CounterTest } from "./counter_test.js";
import { initCounterClient, CounterClient } from "../../src/counter/view/counter_client.js";
import type { ICounter } from "../../src/counter/counter.js";

// Load actual Counter.html and replace template variables with defaults
const counterHtmlPath = resolve(__dirname, "../../src/counter/view/Counter.html");
const counterHtmlRaw = readFileSync(counterHtmlPath, "utf-8");
const fixtureHtml = `<!DOCTYPE html><html><body>${counterHtmlRaw
  .replace("{{counterCssUri}}", "")
  .replace("{{total}}", "0")
  .replace("{{fooBar}}", "")}</body></html>`;

describe("counter_client", () => {
  let postMessageCalls: unknown[];
  let dom: JSDOM;

  beforeEach(() => {
    dom = new JSDOM(fixtureHtml, { url: "http://localhost" });
    postMessageCalls = [];

    // Set up globals for the test
    global.document = dom.window.document;
    global.window = dom.window as unknown as Window & typeof globalThis;
  });

  class CounterClientTest extends CounterTest {
    protected createCounter(): ICounter {
      return initCounterClient({
        postMessage: (m) => postMessageCalls.push(m),
      });
    }

    protected override assertTotal(counter: ICounter, expected: number): void {
      // First: standard domain assertion
      super.assertTotal(counter, expected);

      // Client view adds: verify DOM element has correct text
      const totalEl = document.getElementById("total");
      expect(totalEl?.textContent).toBe(String(expected));

      // initCounterClient sends initial state requests
      const initCalls = [
        { command: "counter.total" },
        { command: "counter.foo.bar" },
      ];

      // Verify postMessage calls based on scenario
      if (expected === 14) {
        // "counter that starts at three, add 4 and 7, yields 14"
        expect(postMessageCalls).toEqual([
          ...initCalls,
          { command: "counter.count", value: 3 },
          { command: "counter.count", value: 4 },
          { command: "counter.count", value: 7 },
        ]);
      } else if (
        expected === 0 &&
        postMessageCalls.some(
          (m: unknown) =>
            typeof m === "object" &&
            m !== null &&
            "command" in m &&
            (m as { command?: string }).command === "counter.reset"
        )
      ) {
        // "reset clears total"
        expect(postMessageCalls).toEqual([
          ...initCalls,
          { command: "counter.count", value: 5 },
          { command: "counter.reset" },
        ]);
      } else {
        // "starts at zero" — only init calls
        expect(postMessageCalls).toEqual(initCalls);
      }
    }
  }

  new CounterClientTest().registerTests();
});
