import { describe, it, expect } from "vitest";
import { submitTransfer } from "../src/transfers";

describe("Submit same-day transfer", () => {
  it("Submit transfer before cutoff time settles same day", () => {
    const before = new Date("2026-01-15T14:00:00-05:00");
    const result = submitTransfer({ amount: 500, payee: "PAYEE-1", now: before });
    expect(result).toEqual({
      status: "accepted",
      settlementWindow: "same-day",
      payee: "PAYEE-1",
      amount: 500,
    });
  });
});
