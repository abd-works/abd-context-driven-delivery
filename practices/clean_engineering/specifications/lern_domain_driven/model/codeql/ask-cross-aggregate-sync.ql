/**
 * @name ask-cross-aggregate-sync
 * @kind problem
 * @id cdd/practice-graph/ask-cross-aggregate-sync
 * @problem.severity warning
 */

import javascript
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "ask-cross-aggregate-sync")
select subject, message, contributor
