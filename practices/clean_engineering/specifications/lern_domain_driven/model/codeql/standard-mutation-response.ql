/**
 * @name standard-mutation-response
 * @kind problem
 * @id cdd/practice-graph/standard-mutation-response
 * @problem.severity warning
 */

import javascript
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "standard-mutation-response")
select subject, message, contributor
