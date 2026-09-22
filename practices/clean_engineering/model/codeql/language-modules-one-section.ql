/**
 * @name language-modules-one-section
 * @kind problem
 * @id cdd/practice-graph/language-modules-one-section
 * @problem.severity warning
 *
 * CodeQL names the class and its source file. Python then reads
 * `.context/module-context.md` for a `## Modules` heading.
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "language-modules-one-section")
select subject, message, contributor
