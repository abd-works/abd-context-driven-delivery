/** Which graph-query rule slugs this pass evaluates. CodeQL overwrites this file. */

predicate requestedRule(string slug) {
  slug = "organize-by-domain-module" or
  slug = "share-domain-logic" or
  slug = "maintain-layer-purity" or
  slug = "use-ubiquitous-language" or
  slug = "cross-layer-method-naming" or
  slug = "preserve-arg-names-across-layers" or
  slug = "property-casing-transform" or
  slug = "consistent-view-naming" or
  slug = "delegate-routes-to-domain-server" or
  slug = "ensure-type-safe-routes" or
  slug = "standard-mutation-response" or
  slug = "implement-domain-entities-correctly" or
  slug = "implement-full-interfaces" or
  slug = "use-valid-package-names" or
  slug = "include-all-external-dependencies" or
  slug = "test-story-driven" or
  slug = "scaffold-test-scripts" or
  slug = "use-thorough-e2e-tests" or
  slug = "one-json-store-per-aggregate" or
  slug = "repository-owns-aggregate-lifecycle" or
  slug = "ask-cross-aggregate-sync"
}
