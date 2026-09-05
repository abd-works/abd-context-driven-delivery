# Rule: System stories group with the closest visible-trigger user story

**Scanner:** AI review

A **system story** — one with no user-visible interaction of its own — does not become a screen on the site map. It is grouped with the closest user story whose visible interaction displays or enacts the system behavior. The grouping is shown as a note inside that screen's box, not as a separate node or arrow target.

## DO

- Attach the system story to the screen whose visible interaction surfaces its result.

  **Example (pass):**
  ```
  [ crowd manager ]
    IA: crowd tree panel | toolbar | filter bar | character detail panel | status bar

    Groups system stories:
    - Load Prism Shell and Module
    - Open Character Crowd Main Workspace
  ```
  *Load Prism Shell and Module* has no visible state of its own; *Open Character Crowd Main Workspace* is the first user-visible state that surfaces the result, so both are listed inside the *crowd manager* screen.

- When a system story's result is split across multiple user-visible screens, group it with the earliest one.

  **Example (pass):** A system story that pre-loads data used on both *crowd manager* and *character detail panel* groups with *crowd manager*, the first screen to show it.

## DO NOT

- Give a system story its own screen box.

  **Example (fail):**
  ```
  [ Load Prism Shell and Module ]
  ```
  This is not a screen — the user never sees a "Load Prism Shell" state.

- Make a system story an arrow target.

  **Example (fail):**
  ```
  [ game directory prompt ] --GM submits valid path--> [ Load Prism Shell and Module ]
  ```
  The transition runs from *game directory prompt* to the next user-visible screen (*crowd manager*), and *Load Prism Shell and Module* is grouped inside that screen.

- Hide a system story entirely.

  **Example (fail):** Omit *Load Prism Shell and Module* from the site map because it has no visible state. It must still appear as a grouped note inside the screen that surfaces it.
