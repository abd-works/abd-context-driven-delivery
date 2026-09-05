# Rule: Actors are situational people or organisations tied to the goal

**Scanner:** Manual review

This check applies to **`ACTOR:`** lines under the mapped **`GOAL:`** in **`impact-map.md`** / **`impact-map.txt`**. **Passing** means each label shows *who* in *what situation* can help or block that goal, split when behaviours differ, and never substitutes systems or products for people. **Failing** means bare categories, personified platforms, or one **`ACTOR:`** bucket hiding incompatible situations.

## DO

- Name actors by situation: segment, lifecycle moment, channel, or context that matters for this goal, not the abstract category alone.

  **Example (pass):** `ACTOR: New mobile shoppers (first order within fourteen days)`.

- Make the situation visible in the label (cohort, geography, tenure, stress moment, contract window).

  **Example (pass):** `ACTOR: Tier-one support agents (queue A, business hours)`.

- Split when situations imply different behaviours under the same broad label.

  **Example (pass):** Separate `ACTOR: Day-one buyer` from `ACTOR: Renewal owner` when impacts differ.

- Keep labels short while still showing who and why the situation matters for the goal.

  **Example (pass):** `ACTOR: Payment acquirer partner (contract renewal window)`.

- Give every **`ACTOR:`** at least one **`IMPACT:`**; merge or drop actors with nothing behavioural to say.

  **Example (pass):** `ACTOR: Streamers in the spring campaign cohort` with at least one `IMPACT:` branch beneath it.

## DO NOT

- Use bare categories with no situation when the map needs distinct behaviours.

  **Example (fail):** `ACTOR: Customers` with impacts that only apply to wholesale buyers, mobile guests, and admins (split or narrow).

- Cast a product, service, system, or platform as the actor.

  **Example (fail):** `ACTOR: The loyalty API` (put the system under **`DELIVERABLE:`**; name the person or team).

- Collapse incompatible situations into **`ACTOR: Users`** when impacts assume different groups or moments.

  **Example (fail):** One `ACTOR: Users` line with impacts that only make sense for parents, teens, and admins respectively.

- Use component names where a person or organisation is what helps or blocks.

  **Example (fail):** `ACTOR: The platform` instead of `ACTOR: Internal platform SRE rotation`.

**Source:** `SKILL.md`, Core concepts / Actors.
