/**
 * @name maintain-layer-purity
 * @kind problem
 * @id cdd/practice-graph/maintain-layer-purity
 * @problem.severity warning
 */

import javascript
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "maintain-layer-purity")
select subject, message, contributor
