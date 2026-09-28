/**
 * @name use-valid-package-names
 * @kind problem
 * @id cdd/practice-graph/use-valid-package-names
 * @problem.severity warning
 */

import javascript
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "use-valid-package-names")
select subject, message, contributor
