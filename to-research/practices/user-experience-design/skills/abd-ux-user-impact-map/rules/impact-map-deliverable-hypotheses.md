# Rule: Deliverables are shippable options under impacts

**Scanner:** Manual review

This check applies to **`DELIVERABLE:`** lines under **`IMPACT:`** in **`impact-map.md`** / **`impact-map.txt`**. **Passing** means each line names a roadmap-sized bet (capability, epic, experiment, policy move) that could plausibly support the parent behaviour, one clear idea per line, with outcome and behaviour language kept in **`GOAL:`**, **`IMPACT:`**, and metrics where they belong. **Failing** means goal proof, vague bundles, non-shippable labels, or behaviour sentences parked under **`DELIVERABLE:`**.

## DO

- Phrase each **`DELIVERABLE:`** as a roadmap-sized option that might create the parent impact.

  **Example (pass):** Under `IMPACT: Share run highlights to social` — `DELIVERABLE: One-tap share sheet with clip`.

- Use several **`DELIVERABLE:`** lines under one impact when they are different bets on the same behaviour.

  **Example (pass):** Same impact lists `DELIVERABLE: Native share extension` and `DELIVERABLE: Post-to-feed template`.

- Keep one shippable idea per line; split merged features.

  **Example (pass):** `DELIVERABLE: Seasonal badge asset pack` (single bet; not combined with unrelated UI work on the same line).

- Mirror the same deliverable names in hypotheses and ASCII outputs when those formats ship for the same engagement.

  **Example (pass):** Hierarchy shows `DELIVERABLE: Queue-time fairness pass`; hypotheses build bullet references the same wording for that feature.

## DO NOT

- Put outcome language, behaviour sentences, or goal numeric proof in **`DELIVERABLE:`** that belong under **`GOAL:`**, **`IMPACT:`**, or on a **`METRIC:`** line under a **`GOAL:`**.

  **Example (fail):** `DELIVERABLE: Verified MAU +20% vs baseline` (that belongs on a **`METRIC:`** under the **`GOAL:`**, not as a shippable option).

- Use a vague grab-bag label instead of concrete options.

  **Example (fail):** `DELIVERABLE: Everything for sharing`.

- Use empty success labels as if they were work.

  **Example (fail):** `DELIVERABLE: Success`.

- Park observable behaviour under **`DELIVERABLE:`** instead of under **`IMPACT:`**.

  **Example (fail):** `DELIVERABLE: User posts weekly` (behaviour belongs under **`IMPACT:`**, not under **`DELIVERABLE:`**).

**Source:** `SKILL.md`, Core concepts / Deliverables.
