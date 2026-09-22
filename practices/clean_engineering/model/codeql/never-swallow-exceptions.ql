/**
 * @name never-swallow-exceptions
 * @kind problem
 * @id cdd/practice-graph/never-swallow-exceptions
 * @problem.severity warning
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "never-swallow-exceptions")
select subject, message, contributor
