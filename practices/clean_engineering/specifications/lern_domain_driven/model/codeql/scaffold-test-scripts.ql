/**
 * @name scaffold-test-scripts
 * @kind problem
 * @id cdd/practice-graph/scaffold-test-scripts
 * @problem.severity warning
 */

import javascript
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "scaffold-test-scripts")
select subject, message, contributor
