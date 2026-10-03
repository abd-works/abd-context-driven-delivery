/**
 * @name implement-full-interfaces
 * @practice lern_domain_driven
 * @fidelity code
 * @node class
 * @id lern_domain_driven/code/implement-full-interfaces
 * @problem.severity warning
 */

import javascript
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "implement-full-interfaces")
select subject, message, contributor
