/**
 * @name test-story-driven
 * @kind problem
 * @id cdd/practice-graph/test-story-driven
 * @problem.severity warning
 */

import javascript
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "test-story-driven")
select subject, message, contributor
