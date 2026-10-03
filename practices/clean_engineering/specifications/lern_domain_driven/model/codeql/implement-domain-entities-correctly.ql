/**
 * @name implement-domain-entities-correctly
 * @practice lern_domain_driven
 * @fidelity code
 * @node class
 * @id lern_domain_driven/code/implement-domain-entities-correctly
 * @problem.severity warning
 */

import javascript
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "implement-domain-entities-correctly")
select subject, message, contributor
