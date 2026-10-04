/** Which graph-query rule slugs this pass evaluates. CodeQL overwrites this file. */

predicate requestedRule(string slug) {
  slug = "flaccid-data-object-no-behavior" or
  slug = "screen-interface-not-a-domain-object" or
  slug = "private-method-naming" or
  slug = "no-orphaned-objects" or
  slug = "domain-concepts-not-technical-names" or
  slug = "service-is-homeless" or
  slug = "repository-is-collection-lifecycle" or
  slug = "load-with-identity-in-hand"
}
