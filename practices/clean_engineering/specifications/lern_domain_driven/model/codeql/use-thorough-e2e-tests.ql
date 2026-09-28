/**
 * @name use-thorough-e2e-tests
 * @kind problem
 * @id cdd/practice-graph/use-thorough-e2e-tests
 * @problem.severity warning
 */

import javascript
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "use-thorough-e2e-tests")
select subject, message, contributor
