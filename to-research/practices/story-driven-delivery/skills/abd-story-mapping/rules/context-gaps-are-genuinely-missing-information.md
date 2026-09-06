# Rule: Context gaps are genuinely missing information

**Scanner:** Manual review

Every entry in the **Context Gaps** section of `story-map.md` / `story-map.txt` states information that is **genuinely unavailable** — a business decision not yet made, a stakeholder perspective not yet gathered, or a technical constraint not yet known. The gap names what is unknown, what options exist, and what depends on the answer. Failure is a gap that the source material already answers, a gap that parks unfinished analysis, a gap outside the product scope, or a gap that questions a decision the user already stated.

## DO

- Before writing a gap, check: "Does the source material answer this?" If yes, finish the analysis — it is unfinished work, not a gap.

  **Example (pass):** Gap: "Settlement currency for cross-border wires — source material covers domestic wires only; need to confirm whether the platform supports multi-currency settlement or converts at initiation." The source genuinely does not answer this.

- Write each gap in plain stakeholder language: what is unknown, what options exist, what depends on the answer.

  **Example (pass):** Gap: "Chargeback handling — two options: (a) platform manages disputes end-to-end, (b) platform routes to external dispute processor. Affects whether we need a dispute resolution epic. Awaiting product owner decision."

- **Verification pass before finalising:** After writing Context Gaps, search the source material for each gap phrase. If the source describes the mechanic, remove the gap and map stories instead.

  **Example (pass):** Draft Context Gaps section included:

  ```
  ## Context Gaps
  - Employee promotion: The source describes performance-review scoring, band-level
    progression, and compensation adjustment. Is promotion workflow in scope?
  ```

  Verification pass finds the source describes the mechanic in detail. Gap removed; stories mapped instead:

  ```
  (E) Process Employee Promotion
      (S) Manager --> Submit Promotion Nomination with Review Scores
      (S) HR --> Validate Band-Level Eligibility
      (S) System --> Adjust Compensation per New Band
  ```

## DO NOT

- Use gaps as a parking lot for analysis you haven't done yet.

  **Example (fail):** Gap: "Transaction rules per account type — not yet mapped." The source material describes IRA contribution limits, margin maintenance calls, and trust beneficiary distributions. This is deferred work, not missing information.

- Flag domain-obvious answers as gaps.

  **Example (fail):** Gap: "Do refund transactions use the same ledger as payments?" when the source material describes a single unified ledger for all transaction types. The answer is in the source — no gap needed.

- Raise concerns outside the product scope unless the user asks.

  **Example (fail):** Gap: "Licensing and redistribution rights for third-party payment network logos." This is legal/business, not product scope.

- Question something the user has already stated as a decision.

  **Example (fail):** Gap: "Should onboarding be self-service or manual?" after the user said "manual onboarding only for now." The user already decided — this is not a gap.

**Scanner heuristic:** Flag gap text containing phrases like "not yet mapped," "is X in scope?," "TBD," or "to be determined" as candidates for false gaps — these phrases often indicate deferred analysis rather than genuinely missing information.

**Source:** Engagement corrections log — root cause B; entry 1.
