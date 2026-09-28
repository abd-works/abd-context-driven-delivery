/**
 * @name include-all-external-dependencies
 * @kind problem
 * @id cdd/practice-graph/include-all-external-dependencies
 * @problem.severity warning
 */

import javascript
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "include-all-external-dependencies")
select subject, message, contributor
