/**
 * @name one-way-deps
 * @kind problem
 * @id cdd/practice-graph/one-way-deps
 * @problem.severity warning
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "one-way-deps")
select subject, message, contributor
