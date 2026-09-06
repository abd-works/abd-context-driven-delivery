# Rule: Affordances and feedback are explicit, named, and trace to AC or UL

**Scanner:** AI review

Every affordance on the wireframe — input, button, list, message area, status indicator — has a name in domain terms and traces back to a specific acceptance criterion or a UL term in scope. Where the acceptance criteria require feedback (success, progress, error, validation), the wireframe shows a labelled region for that feedback. Decorative or speculative affordances are out of scope.

## DO

- Label every affordance using a UL term or copy from an AC clause.

  **Example (pass):** Input labelled `COH game directory path` (UL term); button labelled `Continue` (the AC say "the application proceeds to open the crowd manager"; a `Continue` affordance is justified). Each is traceable.

- Show a labelled region for every feedback type the AC require.

  **Example (pass):** AC mention "fails with a message identifying what is missing" — wireframe shows a labelled `validation error area` region beneath the input.

- Indicate enabled/disabled states the AC require.

  **Example (pass):** AC say the `Continue` action is only available when the path validates — wireframe annotates the `Continue` control as `enabled only when COH game directory is valid`.

## DO NOT

- Add an affordance that no AC or UL term justifies.

  **Example (fail):** Adding a `Reset to defaults` button on the `game directory prompt` because "it might be useful". No AC mentions it; it is invented work.

- Show feedback regions that AC do not require.

  **Example (fail):** Adding a "success animation" region after a valid path is submitted when no AC asks for an animation.

- Imply behaviour through unlabelled shapes.

  **Example (fail):** A red dot at the corner of an input with no label. Either label it as `validation error indicator` (and trace it to an AC), or remove it.
