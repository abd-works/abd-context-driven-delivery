/**
 * @name implement-full-interfaces
 * @kind problem
 * @id cdd/practice-graph/implement-full-interfaces
 * @problem.severity warning
 */

import javascript
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "implement-full-interfaces")
select subject, message, contributor
