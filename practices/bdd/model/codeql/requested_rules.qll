/** Which graph-query rule slugs this pass evaluates. CodeQL overwrites this file. */

predicate requestedRule(string slug) {
  slug = "observable-behavior" or
  slug = "describe-is-subject-not-internal" or
  slug = "state-not-when" or
  slug = "one-assertion-per-test" or
  slug = "layer-isolation"
}
