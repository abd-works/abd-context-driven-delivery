/**
 * @name delegate-routes-to-domain-server
 * @practice lern_domain_driven
 * @fidelity code
 * @node operation
 * @id lern_domain_driven/code/delegate-routes-to-domain-server
 */

import javascript
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "delegate-routes-to-domain-server")
select subject, message, contributor
