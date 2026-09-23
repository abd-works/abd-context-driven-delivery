/** Which graph-query rule slugs this pass evaluates. CodeQL overwrites this file. */

predicate requestedRule(string slug) {
  slug = "do-not-invent-parallel-object-models" or
  slug = "named-seam-and-constraint" or
  slug = "deep-module" or
  slug = "public-seam-only" or
  slug = "use-typed-signatures" or
  slug = "one-way-deps" or
  slug = "low-coupling" or
  slug = "layer-separation" or
  slug = "keep-classes-single-responsibility" or
  slug = "shape-classes-around-resources" or
  slug = "put-logic-on-the-owning-resource" or
  slug = "hide-inner-details" or
  slug = "use-property-not-accessor" or
  slug = "prefer-class-operations" or
  slug = "use-explicit-dependencies" or
  slug = "limit-operation-parameters" or
  slug = "avoid-vague-parameter-names" or
  slug = "limit-comments" or
  slug = "use-intention-revealing-names" or
  slug = "use-consistent-naming" or
  slug = "eliminate-duplication" or
  slug = "keep-operations-small-focused" or
  slug = "simplify-control-flow" or
  slug = "provide-meaningful-context" or
  slug = "use-exceptions-properly" or
  slug = "never-swallow-exceptions"
}
