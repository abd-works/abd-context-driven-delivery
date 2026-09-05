# Rule: Structural accessibility holds at the mockup level

**Scanner:** AI review

Mockup accessibility is structural — heading order is implied by the layout, every input has a visible label drawn from the UL or AC, every error or status message has a labelled region (not just colour), and the layout does not require colour to convey meaning. Prototype-level concerns (contrast, focus ring style, basic labels in the clickable hi-fi) belong to `abd-ux-specification` and are not enforced here.

## DO

- Pair every input with a visible text label, placed adjacent to the input.

  **Example (pass):** `COH game directory path` text label sits above (or before) the input field. The wireframe shows the label even though the visual treatment is not yet decided.

- Convey errors with both a labelled region and explicit text.

  **Example (pass):** The `validation error area` region carries the verbatim error copy from AC — not just a coloured outline.

- Use a clear heading or region title for each major section a screen reader user would expect to land on.

  **Example (pass):** The `prompt panel` region carries the heading copy from the AC: `COH game directory not found or invalid`.

## DO NOT

- Show inputs without labels.

  **Example (fail):** A blank text field with placeholder-only content (e.g. greyed `Enter path...` inside the box). Placeholders are not labels.

- Communicate state through colour alone.

  **Example (fail):** Drawing the input border red to indicate validation failure with no labelled error region nearby.

- Hide required messages behind hover or focus interactions at the mockup stage.

  **Example (fail):** "Error appears in a tooltip when you hover the input". The mockup shows the message region directly; interaction-only revealing belongs to a later pass.
