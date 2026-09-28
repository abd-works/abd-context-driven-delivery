/**
 * @name implement-domain-entities-correctly
 * @kind problem
 * @id cdd/practice-graph/implement-domain-entities-correctly
 * @problem.severity warning
 */

import javascript
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "implement-domain-entities-correctly")
select subject, message, contributor
