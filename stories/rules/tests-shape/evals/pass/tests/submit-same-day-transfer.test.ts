import { describe, it, expect } from "vitest";
import { submitTransfer, currentServerTime } from "../src/transfers";

describe("Submit same-day transfer", () => {
  it("submitting before cutoff marks the transfer as same-day", () => {
    const before = new Date("2026-01-15T14:00:00-05:00");
    const result = submitTransfer({ amount: 500, payee: "PAYEE-1", now: before });
    expect(result.settlementWindow).toBe("same-day");
  });

  it("submitting after cutoff marks the transfer as next-day", () => {
    const after = new Date("2026-01-15T16:00:00-05:00");
    const result = submitTransfer({ amount: 500, payee: "PAYEE-1", now: after });
    expect(result.settlementWindow).toBe("next-day");
  });
});
