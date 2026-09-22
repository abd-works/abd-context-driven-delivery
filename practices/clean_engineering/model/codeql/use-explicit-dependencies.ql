/**
 * @name use-explicit-dependencies
 * @kind problem
 * @id cdd/practice-graph/use-explicit-dependencies
 * @problem.severity warning
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "use-explicit-dependencies")
select subject, message, contributor
