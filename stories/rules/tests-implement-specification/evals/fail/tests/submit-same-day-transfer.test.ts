import { describe, it, expect } from "vitest";
import { submitTransfer } from "../src/transfers";

describe("Submit same-day transfer", () => {
  it("Transfer with negative amount triggers arcane failure", () => {
    const before = new Date("2026-01-15T14:00:00-05:00");
    const result = submitTransfer({ amount: -1, payee: "PAYEE-1", now: before });
    expect(result.status).toBe("rejected");
  });
});
