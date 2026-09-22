/**
 * @name missing-module-context
 * @kind problem
 * @id cdd/practice-graph/missing-module-context
 * @problem.severity warning
 *
 * CodeQL names the class and its source file. Python then checks that the
 * folder owns `.context/module-context.md` — markdown is not in the Python DB.
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "missing-module-context")
select subject, message, contributor
