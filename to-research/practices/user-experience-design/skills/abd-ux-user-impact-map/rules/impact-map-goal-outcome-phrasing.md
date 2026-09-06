# Rule: Goals read as business outcomes with METRIC lines for lagging proof

**Scanner:** Manual review

This check applies to **`GOAL:`** and **`METRIC:`** lines indented under those goals in **`impact-map.md`** / **`impact-map.txt`**. **Passing** means a credible hierarchy (broad to the level you are mapping), each **`GOAL:`** phrased as an outcome in the world, numeric proof on **`METRIC:`** under the level it measures, and headlines that stay directional rather than solution-led. **Failing** means launch-or-build language as the goal, or percent targets baked into the **`GOAL:`** headline when this skill expects them on **`METRIC:`** under that **`GOAL:`**.

## DO

- Model goals as a hierarchy: broader organisational outcomes decompose into finer outcomes that roll up; use one **`GOAL:`** per level you need.

  **Example (pass):** `GOAL: Improve durable growth in the enterprise book` then nested `GOAL: Grow net revenue retention in the enterprise segment`.

- Keep the finest mapped **`GOAL:`** at a workshop-friendly horizon (often about a quarter or less when you timebox).

  **Example (pass):** Under a multi-year headline, the mapped focus is `GOAL: Grow monthly active players` for the next planning slice.

- Phrase each **`GOAL:`** as a business outcome (grow, reduce, achieve, strengthen) with clear object; put lagging proof on **`METRIC:`** under that level.

  **Example (pass):** `GOAL: Accomplish same-day checkout completion for domestic orders` with `METRIC: Same-day rate ninety percent plus (strategic)`.

- Keep each **`GOAL:`** line a directional headline at its altitude; express proof you moved on **`METRIC:`** where you measure.

  **Example (pass):** `GOAL: Grow monthly active players` with `METRIC: Verified MAU +20% vs baseline this quarter` on the lines below that goal.

- Anchor stakes readers recognise: revenue, adoption, risk, compliance, cost, market position, operational reliability.

  **Example (pass):** `GOAL: Reduce fraud loss in card-not-present checkout` under a revenue-and-risk story.

## DO NOT

- Headline the **`GOAL:`** as build, ship, implement, or launch when the real measure is behaviour, revenue, or risk (put the build under **`DELIVERABLE:`**).

  **Example (fail):** `GOAL: Ship checkout v2`.

- Name an output or project as the goal when the goal is the outcome that output is meant to serve.

  **Example (fail):** `GOAL: Build moderation dashboard`.

- Use launch metaphors as the goal instead of the stakeholder outcome.

  **Example (fail):** `GOAL: Mobile app relaunch`.

- Put numeric bars in the **`GOAL:`** headline when this skill expects them on **`METRIC:`** under that outcome.

  **Example (fail):** `GOAL: Grow verified MAU by twenty percent this quarter` (split: short directional **`GOAL:`** plus **`METRIC:`** for the +20% bar).

**Source:** `SKILL.md`, Core concepts / Goal.
