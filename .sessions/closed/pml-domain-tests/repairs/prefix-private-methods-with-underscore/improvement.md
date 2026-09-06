# private-method-naming

- **tool:** Ddd (logged as CleanEngineering on the class diagram)
- **error:** deriveOnboardingStep() shown as public + with no _ prefix. Private helpers must be - _deriveOnboardingStep.
- **rule:** private-method-naming
- **what changed:**
  - **Prose — yes.** Rule bullet on ddd.md building_blocks and templates/ddd-sketch.md.
  - **Detector — yes.** ddd/scanners/private_method_naming_scanner.py.
  - **Generator — no visibility rewriter.** The diagram emitter still prints what the sketch says; the rule tells the AI how to write it.
