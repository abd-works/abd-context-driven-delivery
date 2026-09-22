/**
 * @name prefer-class-operations
 * @kind problem
 * @id cdd/practice-graph/prefer-class-operations
 * @problem.severity warning
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "prefer-class-operations")
select subject, message, contributor
