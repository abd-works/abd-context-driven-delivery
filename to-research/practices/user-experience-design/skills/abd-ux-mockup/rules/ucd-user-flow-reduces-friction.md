# Rule: The wireframe lays out the user flow to reduce friction

**Scanner:** AI review

The wireframe presents the primary user action in the user's eye-path, places prerequisite information where the user looks for it, and does not require the user to scroll or hunt for affordances the acceptance criteria say are required. Friction here means: extra clicks, extra scrolling, ambiguous next steps, or the primary action competing with secondary actions for attention.

## DO

- Put the primary affordance (the one the AC describe as the screen's main outcome) in a single, obvious place.

  **Example (pass):** `Continue` on the `game directory prompt` sits at the bottom-right of the prompt panel, where the user finishes reading the input → error area → action sequence.

- Place prerequisite affordances above or beside the action that consumes them.

  **Example (pass):** The `COH game directory path` input sits above the `Continue` control, not below it.

- Group related affordances into one region (drawn from the initial IA).

  **Example (pass):** `path input` and `Browse...` sit inside the same labelled `path input area` region.

## DO NOT

- Bury the primary action below secondary content, or behind another click.

  **Example (fail):** `Continue` placed below a long block of help text the AC do not require, or hidden inside a menu the AC do not describe.

- Place required affordances off-screen or below the fold of a typical lo-fi viewport.

  **Example (fail):** The `validation error area` rendered below the `Continue` button, so the user cannot see the error and the action that depends on it without scrolling.

- Show competing primary actions.

  **Example (fail):** Two equally prominent buttons — `Continue` and `Save and exit` — when only `Continue` traces to AC. The other is invented and adds friction.
