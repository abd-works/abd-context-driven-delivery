import { describe, it, expect } from "vitest";
import { submitTransfer } from "../src/transfers";

describe("Submit same-day transfer", () => {
  it("Zero-amount transfer is rejected", () => {
    // Bug: BUG-1234 — zero-amount transfers were being accepted and recorded
    const before = new Date("2026-01-15T14:00:00-05:00");
    const result = submitTransfer({ amount: 0, payee: "PAYEE-1", now: before });
    expect(result.status).toBe("rejected");
  });
});
