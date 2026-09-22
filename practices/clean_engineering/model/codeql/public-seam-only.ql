/**
 * @name public-seam-only
 * @kind problem
 * @id cdd/practice-graph/public-seam-only
 * @problem.severity warning
 *
 * CodeQL names the class and its source file. Python then reads
 * `.context/module-context.md` for leaked internals.
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "public-seam-only")
select subject, message, contributor
