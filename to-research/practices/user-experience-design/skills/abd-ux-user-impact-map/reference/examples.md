# Impact Mapping — Examples

## Worked example (live-ops product)

Read as a **hierarchy**. Each `Goal` line carries its **goal metric** in angle brackets. Nested goals roll up. Under the finest goal, each `|- Actor` branch lists **impacts**; after `--`, **Q1 / Q2 / …** (or M1 / M2, quarters, months — name the convention once) are scheduled options for *that* impact only. Every feature still ties to one actor-and-behaviour path.

```text
Strengthen recurring revenue and engagement in the flagship title <net revenue retention; live-ops engagement targets for the title>
|- Grow monthly active players <verified MAU +20% vs baseline; week-over-week return among onboarded>
     |- Existing players (returning, past onboarding)
          Share run highlights to social <share attempts per weekly active player; target cadence at least weekly> -- Q1: One-tap share sheet with clip, Q2: Seasonal tournament badge, Q3: Friend-invite deep link from post-match
          Complete ranked matches regularly <ranked matches per active player per week; target at least three per week> -- Q1: Queue-time fairness pass, Q2: Streak bonus for consistent ranked play
     |- New players (first fourteen days after install)
          Finish onboarding and first ranked match in the first session <session-one ranked completion rate> -- Q1: Guided tutorial path with fewer dead ends, Q2: Optional skip for experienced players on a new device (abuse guardrails TBD)
```

Q1 / Q2 / Q3 here mean calendar quarters for the illustration; use whatever timeboxes the room agrees. Options on a line are different bets on the **same** impact, sequenced by timebox — not a second map.
