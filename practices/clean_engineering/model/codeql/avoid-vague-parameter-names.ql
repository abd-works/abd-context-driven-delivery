/**
 * @name avoid-vague-parameter-names
 * @kind problem
 * @id cdd/practice-graph/avoid-vague-parameter-names
 * @problem.severity warning
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "avoid-vague-parameter-names")
select subject, message, contributor
