/**
 * @name maintain-layer-purity
 * @practice lern_domain_driven
 * @fidelity code
 * @node module
 * @id lern_domain_driven/code/maintain-layer-purity
 */

import javascript
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "maintain-layer-purity")
select subject, message, contributor
