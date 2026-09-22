/**
 * @name limit-operation-parameters
 * @kind problem
 * @id cdd/practice-graph/limit-operation-parameters
 * @problem.severity warning
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "limit-operation-parameters")
select subject, message, contributor
