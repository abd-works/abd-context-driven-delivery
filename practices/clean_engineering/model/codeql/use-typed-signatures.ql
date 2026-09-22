/**
 * @name use-typed-signatures
 * @kind problem
 * @id cdd/practice-graph/use-typed-signatures
 * @problem.severity warning
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "use-typed-signatures")
select subject, message, contributor
