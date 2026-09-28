/**
 * @name consistent-view-naming
 * @kind problem
 * @id cdd/practice-graph/consistent-view-naming
 * @problem.severity warning
 */

import javascript
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "consistent-view-naming")
select subject, message, contributor
