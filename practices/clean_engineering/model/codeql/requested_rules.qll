/** Which graph-query rule slugs this pass evaluates. CodeQL overwrites this file. */

predicate requestedRule(string slug) {
  slug = "prefer-class-operations"
}
