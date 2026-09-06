# Rule: Multi-actor maps record assumptions or explicit none

**Scanner:** Manual review

For one engagement, **`impact-map.md`** and **`impact-map.txt`** (same tree) either make hidden dependencies visible or they fail a quick review. **Passing** means: when two or more distinct **`ACTOR:`** lines appear, the reader sees at least one **`ASSUMPTION:`** that could be tested, or an explicit **none** plus a one-line reason. Every **`DELIVERABLE:`** hangs under a full branch from **`GOAL:`** through **`ACTOR:`** and **`IMPACT:`** in that file. **Failing** means several actors and no **`ASSUMPTION:`** line at all, or **`DELIVERABLE:`** lines that are not anchored in the same tree.

## DO

- When the tree has two or more distinct **`ACTOR:`** lines, include at least one **`ASSUMPTION:`** line that states a testable belief, dependency, or conflict across those branches.

  **Example (pass):** After four **`ACTOR:`** blocks, the file includes `ASSUMPTION: Moderator SLA holds if creator volume stays under X streams per week.`

- When no cross-branch assumption is needed, record that explicitly on one line.

  **Example (pass):** `ASSUMPTION: None identified - wholesale and retail tracks already use separate fulfillment with ops sign-off.`

## DO NOT

- Omit **`ASSUMPTION:`** entirely when two or more **`ACTOR:`** lines appear in the same file.

  **Example (fail):** Five **`ACTOR:`** labels and zero **`ASSUMPTION:`** lines anywhere in the tree.

- Emit **`DELIVERABLE:`** lines that are not under a **`GOAL:`** with **`ACTOR:`** and **`IMPACT:`** ancestors in the same file.

  **Example (fail):** First substantive line is `DELIVERABLE: Mobile relaunch` with no **`GOAL:`** above it.

**Source:** Practice convention. Pair with **`rules/impact-map-phased-backlog-actor-impact.md`** for phased backlog **Actor / impact** cells.
