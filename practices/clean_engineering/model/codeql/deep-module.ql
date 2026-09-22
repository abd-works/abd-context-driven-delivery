/**
 * @name deep-module
 * @kind problem
 * @id cdd/practice-graph/deep-module
 * @problem.severity warning
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "deep-module")
select subject, message, contributor
