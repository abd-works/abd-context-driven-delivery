/**
 * @name property-casing-transform
 * @practice lern_domain_driven
 * @fidelity code
 * @node property
 * @id lern_domain_driven/code/property-casing-transform
 */

import javascript
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "property-casing-transform")
select subject, message, contributor
