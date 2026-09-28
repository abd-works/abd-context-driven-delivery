/**
 * @name cross-layer-method-naming
 * @kind problem
 * @id cdd/practice-graph/cross-layer-method-naming
 * @problem.severity warning
 */

import javascript
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "cross-layer-method-naming")
select subject, message, contributor
