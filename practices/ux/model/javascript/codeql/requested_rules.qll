/** Which graph-query rule slugs this pass evaluates. CodeQL overwrites this file. */

predicate requestedRule(string slug) {
  slug = "story-domain-js-imported" or
  slug = "key-interactions-wired" or
  slug = "screen-names-use-domain-terms"
}
