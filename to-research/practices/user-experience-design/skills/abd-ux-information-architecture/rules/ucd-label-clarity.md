# Rule: Labels are clear, single-purpose, and consistently named

**Scanner:** AI review

Every screen name, region name, and transition label on the site map is unambiguous, names one thing, and is reused exactly the same way wherever it appears. Different labels never refer to the same screen or region; the same label never refers to two different things. Names are short noun phrases (or, for transitions, short trigger phrases) drawn from the Domain Language.

## DO

- Use the same label for the same screen everywhere on the canvas, including inside grouped-story notes.

  **Example (pass):** A transition arrow points to a screen labeled `crowd manager`; a grouped note elsewhere on the canvas references the same screen as `crowd manager`. Identical wording.

- Use short trigger phrases for transitions — one user action or one system event in domain terms.

  **Example (pass):** `GM submits valid path`, `crowd repository finished loading`, `GM selects character`.

- When two stories share a screen, use one screen name; do not split the screen for readability.

  **Example (pass):** *Open Character Crowd Main Workspace* and *Load Prism Shell and Module* both surface inside the same `crowd manager` screen.

## DO NOT

- Use two different labels for the same screen.

  **Example (fail):**
  ```
  [ crowd manager ]                [ crowd library ]   ← same screen, different name
  ```

- Reuse one label for two different screens.

  **Example (fail):** Two different boxes both labeled `crowd manager`, one of which is actually the *character detail panel*.

- Write transition labels that combine multiple triggers.

  **Example (fail):** `GM submits path or system finds stored path and validates and loads crowd repository`. Split it; one trigger per arrow.

- Pad labels with adjectives that are not in the UL.

  **Example (fail):** `the main crowd manager dashboard view`. The UL term is `crowd manager`; everything else is invented.
