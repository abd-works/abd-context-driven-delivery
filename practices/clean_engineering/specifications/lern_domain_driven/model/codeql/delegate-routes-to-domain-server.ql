/**
 * @name delegate-routes-to-domain-server
 * @kind problem
 * @id cdd/practice-graph/delegate-routes-to-domain-server
 * @problem.severity warning
 */

import javascript
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "delegate-routes-to-domain-server")
select subject, message, contributor
