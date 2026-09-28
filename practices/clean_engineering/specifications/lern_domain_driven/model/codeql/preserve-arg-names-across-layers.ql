/**
 * @name preserve-arg-names-across-layers
 * @kind problem
 * @id cdd/practice-graph/preserve-arg-names-across-layers
 * @problem.severity warning
 */

import javascript
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "preserve-arg-names-across-layers")
select subject, message, contributor
