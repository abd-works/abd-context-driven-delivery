/** Which graph-query rule slugs this pass evaluates. CodeQL overwrites this file. */

predicate requestedRule(string slug) {
  slug = "keep-classes-single-responsibility" or
  slug = "keep-operations-small-focused" or
  slug = "limit-operation-parameters" or
  slug = "avoid-vague-parameter-names" or
  slug = "simplify-control-flow" or
  slug = "never-swallow-exceptions" or
  slug = "use-exceptions-properly" or
  slug = "use-explicit-dependencies" or
  slug = "use-property-not-accessor" or
  slug = "prefer-class-operations" or
  slug = "prefer-instance-operations" or
  slug = "hide-inner-details" or
  slug = "low-coupling" or
  slug = "shape-classes-around-resources" or
  slug = "put-logic-on-the-owning-resource" or
  slug = "use-typed-signatures" or
  slug = "provide-meaningful-context" or
  slug = "deep-module" or
  slug = "one-way-deps" or
  slug = "extensions-live-with-the-domain" or
  slug = "layer-separation" or
  slug = "missing-module-context" or
  slug = "language-modules-one-section" or
  slug = "public-seam-only" or
  slug = "modules-not-model-blocks"
}
