/**
 * @name organize-by-domain-module
 * @kind problem
 * @id cdd/practice-graph/organize-by-domain-module
 * @problem.severity warning
 */

import javascript
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "organize-by-domain-module")
select subject, message, contributor
