/**
 * @name provide-meaningful-context
 * @kind problem
 * @id cdd/practice-graph/provide-meaningful-context
 * @problem.severity warning
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "provide-meaningful-context")
select subject, message, contributor
