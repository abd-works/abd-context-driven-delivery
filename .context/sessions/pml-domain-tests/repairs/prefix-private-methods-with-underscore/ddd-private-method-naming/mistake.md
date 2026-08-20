# ddd-private-method-naming

- **entry_id:** 7f80b771
- **artifact:** tests/domain/.context/domain-model.drawio
- **rule:** (ddd) private-method-naming
- **wrong:** deriveOnboardingStep() is shown as a public method with + prefix. Internal/private methods must use - visibility and _ prefix (e.g., _deriveOnboardingStep). It is also missing the interaction notation on onboardingStep showing it delegates to this method.
- **status:** fixed
