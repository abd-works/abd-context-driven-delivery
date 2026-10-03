/**
 * @name public-seam-only
 * @practice clean_engineering
 * @fidelity modules
 * @node module
 * @id clean_engineering/modules/public-seam-only
 * @problem.severity warning
 * CodeQL names the class and its source file. Python then reads
 * `.context/module-context.md` for leaked internals.
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "public-seam-only")
select subject, message, contributor
