/**
 * @name share-domain-logic
 * @practice lern_domain_driven
 * @fidelity code
 * @node class
 * @id lern_domain_driven/code/share-domain-logic
 */

import javascript
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "share-domain-logic")
select subject, message, contributor
