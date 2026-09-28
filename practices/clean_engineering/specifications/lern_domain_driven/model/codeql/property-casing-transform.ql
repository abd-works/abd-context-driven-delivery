/**
 * @name property-casing-transform
 * @kind problem
 * @id cdd/practice-graph/property-casing-transform
 * @problem.severity warning
 */

import javascript
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "property-casing-transform")
select subject, message, contributor
