// test/counter/counter.test.ts
import { describe, beforeEach, expect } from "vitest";
import * as fs from "fs";
import * as path from "path";
import * as os from "os";
import { Counter } from "../../src/counter/counter.js";
import { CounterServer } from "../../src/counter/counter_server.js";
import { CounterTest } from "./counter_test.js";
import type { ICounter } from "../../src/counter/counter.js";

/**
 * Domain layer tests.
 * createCounter() returns a plain Counter — no persistence, no view.
 */
export class DomainCounterTest extends CounterTest {
  protected createCounter(): ICounter {
    return new Counter();
  }
}

describe("Counter", () => {
  new DomainCounterTest().registerTests();
});

/**
 * Server domain tests.
 * Uses temp directory for persistence; assertTotal verifies file reload.
 */
describe("CounterServer", () => {
  let tmpDir: string;
  let filePath: string;

  beforeEach(() => {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "counter-"));
    filePath = path.join(tmpDir, "counter.json");
  });

  class ServerCounterTest extends CounterTest {
    protected createCounter(): ICounter {
      return new CounterServer(filePath);
    }

    protected override assertTotal(counter: ICounter, expected: number): void {
      // First: standard domain assertion
      super.assertTotal(counter, expected);

      // Server domain adds: verify persistence by reloading from file
      const reloaded = new CounterServer(filePath);
      expect(reloaded.total).toBe(expected);
    }
  }

  new ServerCounterTest().registerTests();
});
