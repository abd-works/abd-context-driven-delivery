/**
 * @name repository-owns-aggregate-lifecycle
 * @kind problem
 * @id cdd/practice-graph/repository-owns-aggregate-lifecycle
 * @problem.severity warning
 */

import javascript
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "repository-owns-aggregate-lifecycle")
select subject, message, contributor
