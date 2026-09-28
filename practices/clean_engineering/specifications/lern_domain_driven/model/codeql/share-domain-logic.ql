/**
 * @name share-domain-logic
 * @kind problem
 * @id cdd/practice-graph/share-domain-logic
 * @problem.severity warning
 */

import javascript
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "share-domain-logic")
select subject, message, contributor
