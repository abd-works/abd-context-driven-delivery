/**
 * @name hide-inner-details
 * @kind problem
 * @id cdd/practice-graph/hide-inner-details
 * @problem.severity warning
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "hide-inner-details")
select subject, message, contributor
