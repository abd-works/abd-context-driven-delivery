/**
 * @name standard-mutation-response
 * @practice lern_domain_driven
 * @fidelity code
 * @node operation
 * @id lern_domain_driven/code/standard-mutation-response
 */

import javascript
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "standard-mutation-response")
select subject, message, contributor
