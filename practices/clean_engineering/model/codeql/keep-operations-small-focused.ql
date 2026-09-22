/**
 * @name keep-operations-small-focused
 * @kind problem
 * @id cdd/practice-graph/keep-operations-small-focused
 * @problem.severity warning
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "keep-operations-small-focused")
select subject, message, contributor
