/**
 * @name one-json-store-per-aggregate
 * @practice lern_domain_driven
 * @fidelity code
 * @node class
 * @id lern_domain_driven/code/one-json-store-per-aggregate
 */

import javascript
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "one-json-store-per-aggregate")
select subject, message, contributor
