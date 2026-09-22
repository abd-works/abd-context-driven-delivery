/**
 * @name keep-classes-single-responsibility
 * @kind problem
 * @id cdd/practice-graph/keep-classes-single-responsibility
 * @problem.severity warning
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "keep-classes-single-responsibility")
select subject, message, contributor
