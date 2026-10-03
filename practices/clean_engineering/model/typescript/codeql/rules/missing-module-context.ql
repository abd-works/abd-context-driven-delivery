/**
 * @name missing-module-context
 * @practice clean_engineering
 * @fidelity modules
 * @node module
 * @id clean_engineering/modules/missing-module-context
 * CodeQL names the class and its source file. Python then checks that the
 * folder owns `.context/module-context.md` — markdown is not in the Python DB.
 */

import javascript
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "missing-module-context")
select subject, message, contributor
