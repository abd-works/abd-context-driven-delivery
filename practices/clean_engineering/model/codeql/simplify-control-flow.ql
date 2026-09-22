/**
 * @name simplify-control-flow
 * @kind problem
 * @id cdd/practice-graph/simplify-control-flow
 * @problem.severity warning
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "simplify-control-flow")
select subject, message, contributor
