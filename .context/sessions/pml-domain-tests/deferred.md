# Deferred

Mistakes that cannot be failed with a test under current conditions.
They still live under `mistakes/{folder}/` (open mistakes stay there). This
table is that subset only — not every folder in `mistakes/`.

| folder | entry_id | rule | why deferred |
| --- | --- | --- | --- |
| artifacts-mirror-story-hierarchy | 37da966a | artifacts-mirror-story-hierarchy | Scanner already requires epic/sub-epic/story path segments; Playwright `*.e2e.ts` is not in the suite glob, so the single-file wrapper folder cannot be failed as a distinct RED. |
| authentication-service-separation-2 | 69938788 | authentication-service-separation-2 | E2E form vs auth-flow split is a test-driver design judgment, not a DDD token scan. |
| bc-by-lifecycle-frequency-not-ui-themes | 16d02616 | bc-by-lifecycle-frequency-not-ui-themes | Partitioning BCs by lifecycle vs UI themes is modelling judgment, not a token scan. |
| billing-subscription-stereotypes-wrong | 72edc6f8 | billing-subscription-stereotypes-wrong | Correct Billing/Subscription/Invoice stereotypes require domain identity tests. |
| cart-billing-under-subscription-bc | a7f42c77 | cart-billing-under-subscription-bc | This product's BC placement, not a general CDD rule. |
| cart-repository-not-a-domain-concept | b85a8c64 | cart-repository-not-a-domain-concept | Rejecting CartRepository as a concept is expert-language judgment. |
| change-frequency-as-bc-indicator | f2f5167d | change-frequency-as-bc-indicator | Lifecycle change-frequency as a BC split is modelling judgment. |
| checkout-service-misplaced | 0d1d9c44 | checkout-service-misplaced | Whether CheckoutService is homeless needs aggregate-ownership judgment. |
| clean-engineering-physical-folder-single-boundary-cohesive-f | 3127a00c | physical-folder + artifacts-mirror (stories half) | Kind-bucketed `domain-model/` vs `tiers/e2e/` is mixed CE+stories; CE physical-folder is owned elsewhere; stories scanner cannot fail this folder-kind layout. |
| ddd-correct-stereotype | 2e50418c | ddd-correct-stereotype | Judging Catalog as Aggregate Root vs Domain Service needs domain meaning, not a token pattern. |
| ddd-inheritance-hierarchy | 5d57e45e | ddd-inheritance-hierarchy | Missing Customer←Prospect/Subscriber generalisation is a modelling choice, not a local syntax fail. |
| ddd-invented-types-not-domain-concepts | 6f91af0f | ddd-invented-types-not-domain-concepts | Whether OrderResult/OrderRepository are real concepts needs model judgment. |
| ddd-service-should-be-aggregate-operation | 2b5d320b | ddd-service-should-be-aggregate-operation | Homeless vs aggregate-owned operations need semantic placement judgment. |
| ddd-service-should-be-aggregate-operation-2 | 5e809e0e | ddd-service-should-be-aggregate-operation | Same class: form-field service vs Credentials behavior is not mechanical. |
| ddd-ubiquitous-language | 2c6bd516 | ddd-ubiquitous-language | Expert vocabulary (PortabilityRequest vs ported TelephoneNumber) is not a deterministic scan. |
| diagnose-flaky-visual-bugs-via-playwright-screenshots-and-co | f13c9a7e | diagnose-flaky-visual-bugs | Product/library bug in PlanSelector (pml-harmony); not a context-tool rule. |
| diagram-aggregate-layout-cohesion | e3f08080 | diagram-aggregate-layout-cohesion | Aggregate clustering is spatial judgment. |
| diagram-repository-aggregation-relationship | 299843ab | diagram-repository-aggregation-relationship | Repo diamond/stereotype presence is mixed layout+UML judgment. |
| diagram-stereotype-placement-and-style | 0a1ec6fd | diagram-stereotype-placement-and-style | Stereotype line/weight placement is visual judgment; do not contest drawio scanners. |
| domain-surface-consistency | 938810d7 | domain-surface-consistency | ParadiseMobile surface naming is this product's API, not a general CE scan. |
| every-given-when-then-step-across-every-story-must-be-verb-n | 373093cd | every GWT step verb-noun traced to DDD | `verb-noun-format` only checks map names; exhaustive step→operation mapping is not deterministic. |
| explore-full-interaction-surface | fddaf0b1 | explore-full-interaction-surface | Coverage of the full UI interaction surface is judgment (walk the screen); rule already on Stories. |
| explore-full-interaction-surface-2 | 820c2d24 | explore-full-interaction-surface | Same class as fddaf0b1. |
| harvest-full-domain-inventory-from-sketch | 3211dd7d | harvest-full-domain-inventory-from-sketch | Completeness of harvested types vs a sketch is judgment. |
| invented-types-not-in-code | 15da55fb | invented-types-not-in-code | Comparing model names to a live codebase is out of band for a DDD sketch scanner. |
| missing-relationships-and-orphans | ece21a62 | missing-relationships-and-orphans | Mix of true orphans, standalone VOs, and unjustified repos — not one mechanical pattern. |
| module-spatial-cohesion | a1c0e4b2 | module-spatial-cohesion | Edge-label corridors and wrapping are spatial judgment. |
| number-port-invented-not-in-code | 72515be2 | number-port-invented-not-in-code | NumberPort vs code requires cross-repo presence judgment. |
| onboarded-flag-on-customer-entity | 2775a352 | onboarded-flag-on-customer-entity | This product's Customer flag, not a general DDD rule. |
| one-meaning-per-context | 60818009 | one-meaning-per-context | Rule already on Ddd; this instance is Shared Kernel peer-card layout judgment. |
| physical-folder-2 | 4fc95467 | physical-folder-2 session summary md | Extending physical-folder is owned elsewhere (`physical_folder_scanner.py` / `module_scanners_spec.py` locked). |
| physical-folder-3 | bd5f2222 | physical-folder-3 stopped mid-tree | Arbitrary documentation depth vs cohesive units is judgment, not a deterministic folder scan. |
| reconcile-live | b7e21f4d | reconcile-live | Live vs sketch drift is process/runtime, not a CDD scan. |
| reconcile-live-against-sandbox | cf3d876e | reconcile-live-against-sandbox | Same class: live vs sandbox drift. |
| reconcile-live-against-sandbox-2 | da130f62 | reconcile-live-against-sandbox | Same class. |
| reconcile-live-against-sandbox-3 | 51bfe5ea | reconcile-live-against-sandbox | Live Continue→verify-id vs sandbox `/onboarding/profile` is process/runtime drift. |
| reconcile-live-against-sandbox-4 | 121683f3 | reconcile-live-against-sandbox | Same class. |
| reconcile-live-against-sandbox-5 | b0dfee62 | reconcile-live-against-sandbox | Same class. |
| reconcile-live-against-sandbox-6 | 83a71d38 | reconcile-live-against-sandbox | Same class. |
| seed-prior-story-state | f5536ccb | seed-prior-story-state | Logged error is garbled; no fail-first fixture. |
| separate-concerns | df92e741 | separate-concerns | Cart vs KYC hop is this product's test design, not a general scanner. |
| stories | c9d4e812 | capture-all-scenarios-not-just-happy-path | Same as explore-full-interaction-surface — rule already on Stories; coverage is judgment. |
| stub-fidelity-mirrors-real-api-contract | be9d29f7 | stub-fidelity-mirrors-real-api-contract | Product sandbox stub default; not a CDD generate rule. |
| subscription-invariant-of-subscriber | 541e5118 | subscription-invariant-of-subscriber | Whether Subscription is an invariant of Subscriber is tactical DDD judgment. |
| value-object-composition-misuse | d11858d4 | value-object-composition-misuse | Which VO–VO links should be association vs composition is a design judgment. |
| when-a-story-references-a-deep-link-parameterized-route-e-g- | 69fa6dc1 | deep-link arrival explanation | Whether `/sign-up/:planId` is in-app vs marketing vs wizard hop needs product/flow reading. |
| when-adding-an-env-var-driven-toggle-to-playwright-test-infr | 8e544d0c | Playwright PWDEBUG reserved env | No Playwright helper in this clone to fail-first a reserved-name collision. |
