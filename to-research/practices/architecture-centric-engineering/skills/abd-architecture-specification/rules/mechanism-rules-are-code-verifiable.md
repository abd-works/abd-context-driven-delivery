---
scanner: mechanism-rules-code-verifiable
---

### Rule: Each rule in a mechanism is verifiable by reading code

Every bullet in a mechanism's Rules section MUST be a property a reviewer can confirm or refute by reading code in the mechanism's folder or its composition root. Sentiments — "prefer", "should consider", "is generally a good idea", "strive for", "avoid where possible" — are not rules: they cannot fail a review and they do not constrain new instances. A real mechanism rule names a must or must-never with a specific, findable code-level violation. Passing means a reviewer could point at a file and say "this rule is broken at line N". Failing means a rule restates a principle without a falsifiable code condition.

#### DO

- Write each rule as a must / must-never with a code-visible violation.

  **Example (pass):**
  ```markdown
  ### Rules

  - **Every handler registers in `/src/composition.ts` only.** A handler
    constructed at use-site bypasses the mechanism and is the violation.
  - **No handler imports another handler.** Cross-handler calls go through
    the orchestrator at the composition root; an `import` from one handler
    folder to another is the violation.
  - **Each handler exposes exactly one public function.** Multiple exported
    operations indicate the handler is doing two jobs and must be split.
  ```

- Name the file or pattern that constitutes the violation, so the rule is grep-checkable.

  **Example (pass):** "No handler calls `axios` directly — every outbound HTTP call goes through `/src/services/Axios/AxiosFactory.ts`. A `from 'axios'` import inside `/src/integrations/**/` is the violation."

#### DO NOT

- Write rules that cannot be falsified by reading code.

  **Example (fail):**
  ```markdown
  - **Prefer clear naming.** Choose names that reflect the domain.
  - **Strive for loose coupling.** Components should be independent.
  - **Aim for testability.** Write code that is easy to test.
  ```
  None of these can fail a review. Whose definition of "clear"? What does "strive" mean? They are sentiments, not constraints.

- Restate generic engineering advice as if it were mechanism-specific.

  **Example (fail):** "**Follow SOLID principles.**" — true everywhere; constrains nothing about this mechanism. Drop it.

- Mix rules with rationale that hides the constraint.

  **Example (fail):** "**Handlers should be small because large handlers are hard to test and tend to accumulate responsibilities over time, which causes maintenance burden as the team grows.**" — what is "small"? 50 lines? 5? The rule has dissolved into prose.

**Source:** A rule that cannot fail is not a rule; mechanism rules are the contract that keeps new instances uniform.
