# encode-deferred-modelling-into-generating-tools

- **tool:** Ddd, Stories, CleanEngineering, Drawio
- **error:** Deferred items were parked as "AI judgment" instead of teaching the generating tool how to split contexts, place operations, name types, and draw cards.
- **rule:** bc-by-lifecycle-not-ui-themes, repository-is-collection-lifecycle, shared-identity-is-generalisation, gwt-steps-trace-to-domain-operations, reconcile-live-immediately, explain-deep-link-arrival, stereotype-above-class-name, artifacts-mirror-story-hierarchy, plus tighter existing bullets
- **what changed:**
  - **Prose — yes.** `ddd.md`: contexts split by language and change-frequency, not UI themes; Repository only when there is a collection lifecycle; Catalog is Aggregate Root not Service; CheckoutService.placeOrder is `Cart.checkout`; experts' words (`TelephoneNumber.port`, not `PortabilityRequest`); harvest the whole sketch; Prospect/Subscriber generalise Customer. `stories.md`: `{epic}/{sub-epic}/{story}.{tier}.ts` (no story folder); every GWT step traces to a domain operation; live walk wins; deep-link arrival is explained. `context-as-code-strategy.md` / Stories: tests follow the story map, domain follows `{bc}/{aggregate}/` — not kind-buckets (`domain-model/` vs `tiers/e2e/`). `clean_engineering.md`: physical-folder does not stop mid-tree; VO–VO is association not composition. `drawio.md`: stereotype above the name; cluster root+members+repo; repo diamond.
  - **Sketch / template / example — yes.** `ddd-sketch.md`, `bounded-context-template.md`, Shop example Catalog vs Sales scopes.
  - **Detector — yes.** `stereotype-above-class-name` scanner. `artifacts-mirror-story-hierarchy` already requires the one-file path. Generator `_build_class_html` puts tactical tags in italic above `<b>name</b>`.
  - **Generator — yes.** Drawio class HTML no longer concatenates `<<Stereotype>>` onto the bold title.
  - **Prose — yes (follow-up).** `gwt-steps-trace-to-domain-operations`: a hop to the next step is a named operation on the arriving aggregate (`prospect.verifyIdentity()`), not a route, `waitForCompletion()`, or driving the next concern through the previous aggregate.
