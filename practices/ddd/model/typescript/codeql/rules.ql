/**
 * @name practice-graph-rules
 * @kind problem
 * @id cdd/practice-graph/rules
 * @problem.severity warning
 *
 * One query for every graph rule in this pack. `requestedRule` selects
 * which slugs this pass evaluates; each row still names its rule.
 */

import javascript
import subject_filter
import requested_rules
import rule_hits

from AstNode subject, string message, AstNode contributor, string slug
where
  requestedRule(slug) and
  graphRuleHit(subject, message, contributor, slug)
select subject, message, contributor, slug
