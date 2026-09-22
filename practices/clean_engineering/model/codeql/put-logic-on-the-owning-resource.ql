/**
 * @name put-logic-on-the-owning-resource
 * @kind problem
 * @id cdd/practice-graph/put-logic-on-the-owning-resource
 * @problem.severity warning
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "put-logic-on-the-owning-resource")
select subject, message, contributor
