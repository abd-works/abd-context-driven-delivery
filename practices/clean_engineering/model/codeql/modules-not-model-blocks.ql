/**
 * @name modules-not-model-blocks
 * @kind problem
 * @id cdd/practice-graph/modules-not-model-blocks
 * @problem.severity warning
 *
 * CodeQL names the class and its source file. Python then reads
 * `.context/module-context.md` for typed dumps that belong at model.
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "modules-not-model-blocks")
select subject, message, contributor
