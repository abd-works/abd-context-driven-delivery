# Rule: Phased backlog rows name the same actor and impact as the tree

**Scanner:** Manual review

This check applies to optional phased backlog tables in the same file as the **`GOAL:`** / **`ACTOR:`** / **`IMPACT:`** tree (**`impact-map.md`** / **`impact-map.txt`**). **Passing** means each row's **Actor / impact** cell repeats the **`ACTOR:`** label and **`IMPACT:`** line that branch already contains (same wording or obvious paraphrase), and the timebox convention is named once (for example in **`NOTE:`**). **Failing** means a scheduled feature paired with an actor/impact pair that does not appear in the tree, or silent mixing of timebox schemes.

## DO

- For each phased row, fill the **Actor / impact** column so it matches one **`ACTOR:`** + **`IMPACT:`** path in that file.

  **Example (pass):** Tree contains `ACTOR: Existing players` and `IMPACT: Share run highlights to social`; backlog row `M1 | Share sheet with clip | Existing players / Share run highlights to social`.

- Use one timebox convention per file (for example M1..M4 or Q1..Q4) and record it in **`NOTE:`** once.

  **Example (pass):** `NOTE: M1-M4 below = calendar months in this example; use quarters if the brief says Q1-Q4.`

## DO NOT

- List a feature whose **Actor / impact** cell does not match any actor-and-impact branch in the tree.

  **Example (fail):** Backlog cell `Streamers / Daily clip` when the tree only has `IMPACT: Broadcast this title during the campaign window`.

- Switch timebox schemes row by row without stating the convention.

  **Example (fail):** Mixing `M1`, `Q2`, `Sprint 4` in the same phased table with no **`NOTE:`** explaining the scheme.

**Source:** Practice convention.
