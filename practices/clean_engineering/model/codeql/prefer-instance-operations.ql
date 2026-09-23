/**
 * @name prefer-instance-operations
 * @kind problem
 * @id cdd/practice-graph/prefer-instance-operations
 * @problem.severity warning
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "prefer-instance-operations")
select subject, message, contributor
