/** Which graph-query rule slugs this pass evaluates. CodeQL overwrites this file. */

predicate requestedRule(string slug) {
  slug = "screen-names-use-domain-terms" or
  slug = "story-domain-js-imported" or
  slug = "key-interactions-wired"
}
