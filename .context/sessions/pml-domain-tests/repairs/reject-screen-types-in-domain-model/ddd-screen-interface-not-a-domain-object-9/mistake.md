# ddd-screen-interface-not-a-domain-object-9

- **entry_id:** 09a3b109
- **artifact:** tests/domain/change-plan/change-plan.ts (ChangePlan interface)
- **rule:** (ddd) screen-interface-not-a-domain-object
- **wrong:** ChangePlan modeled as its own wizard interface with open(), openFromServices(), waitForCatalog(), isSelectPlanShowing(), selectPlan(), isConfirmShowing(), acceptTerms(), confirmChange() — a screen driver. Changing plan is an operation on Subscription (changePlan(bundleId)).
- **status:** fixed
