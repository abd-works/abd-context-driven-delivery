/**
 * @name one-json-store-per-aggregate
 * @kind problem
 * @id cdd/practice-graph/one-json-store-per-aggregate
 * @problem.severity warning
 */

import javascript
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "one-json-store-per-aggregate")
select subject, message, contributor
