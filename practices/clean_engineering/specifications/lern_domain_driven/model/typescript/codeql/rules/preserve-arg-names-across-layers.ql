/**
 * @name preserve-arg-names-across-layers
 * @practice lern_domain_driven
 * @fidelity code
 * @node parameter
 * @id lern_domain_driven/code/preserve-arg-names-across-layers
 */

import javascript
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "preserve-arg-names-across-layers")
select subject, message, contributor
