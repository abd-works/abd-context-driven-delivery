# Rule: Impact lines name observable behaviour for the actor

**Scanner:** Manual review

This check applies to **`IMPACT:`** lines under each **`ACTOR:`** in **`impact-map.md`** / **`impact-map.txt`**. **Passing** means each line answers how behaviour should change in a way someone could observe or measure, verb-led, one movement per line, with quotas and numeric bars on **`METRIC:`** lines indented under that **`IMPACT:`** instead of crammed into the headline. **Failing** means feature titles, components, or slogans with no observable picture.

## DO

- Answer how this actor's behaviour should change in terms a reviewer could witness without opening a backlog tool.

  **Example (pass):** `IMPACT: Completes payment on mobile without switching to desktop when the bank supports in-app 3-D Secure.`

- Lead with a verb the actor performs (completes, submits, shares, invites, triages, opts in, returns, finishes).

  **Example (pass):** `IMPACT: Shares run highlights to social`.

- Keep the **`IMPACT:`** headline free of cadence quotas, day-N deadlines, SLA timing, and numeric bars; put those on **`METRIC:`** under that **`IMPACT:`**.

  **Example (pass):** `IMPACT: Opens every abuse report within one business day` with cadence detail moved to `METRIC: Median hours to first action; target under twelve`.

- State one behaviour movement per **`IMPACT:`**; split when two behaviours are mixed.

  **Example (pass):** Split `IMPACT: Finishes tutorial` and `IMPACT: Completes first ranked match` when they are two movements.

- Keep channel or qualitative guardrails in the impact phrase when they are not numeric bars (for example *without calling support*).

  **Example (pass):** `IMPACT: Submits the order without calling support`.

## DO NOT

- Put system names, epic codes, or feature titles alone in **`IMPACT:`** with no behaviour clause.

  **Example (fail):** `IMPACT: New share sheet`.

- Use a component or tool name as if it were behaviour.

  **Example (fail):** `IMPACT: Moderation tool`.

- Ship slogans with no observable picture.

  **Example (fail):** `IMPACT: Better onboarding`.

- Mix two incompatible behaviours in one **`IMPACT:`** line.

  **Example (fail):** `IMPACT: Onboards faster and invites three friends in week one` (split if those are separate movements).

**Source:** `SKILL.md`, Core concepts / Impacts and Purpose (four questions).
