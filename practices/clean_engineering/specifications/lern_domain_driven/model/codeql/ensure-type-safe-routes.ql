/**
 * @name ensure-type-safe-routes
 * @kind problem
 * @id cdd/practice-graph/ensure-type-safe-routes
 * @problem.severity warning
 */

import javascript
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "ensure-type-safe-routes")
select subject, message, contributor
