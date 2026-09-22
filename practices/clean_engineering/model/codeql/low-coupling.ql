/**
 * @name low-coupling
 * @kind problem
 * @id cdd/practice-graph/low-coupling
 * @problem.severity warning
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "low-coupling")
select subject, message, contributor
