/** Which graph-query rule slugs this pass evaluates. CodeQL overwrites this file. */

predicate requestedRule(string slug) {
  slug = "vocabulary-traces-to-domain-source" or
  slug = "verb-noun-format" or
  slug = "story-name-captures-system-mechanic" or
  slug = "four-to-nine-children" or
  slug = "right-size-story-nodes" or
  slug = "gwt-steps-trace-to-domain-operations" or
  slug = "plain-english-gwt-steps"
}
