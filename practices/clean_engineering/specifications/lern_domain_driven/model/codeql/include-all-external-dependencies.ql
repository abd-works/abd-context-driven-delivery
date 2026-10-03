/**
 * @name include-all-external-dependencies
 * @practice lern_domain_driven
 * @fidelity code
 * @node module
 * @id lern_domain_driven/code/include-all-external-dependencies
 */

import javascript
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "include-all-external-dependencies")
select subject, message, contributor
