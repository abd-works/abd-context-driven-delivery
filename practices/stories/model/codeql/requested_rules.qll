/** Which graph-query rule slugs this pass evaluates. CodeQL overwrites this file. */

predicate requestedRule(string slug) {
  slug = "verb-noun-format" or
  slug = "story-name-captures-system-mechanic" or
  slug = "gwt-steps-trace-to-domain-operations" or
  slug = "plain-english-gwt-steps"
}
