/**
 * @name scaffold-test-scripts
 * @practice lern_domain_driven
 * @fidelity code
 * @node module
 * @id lern_domain_driven/code/scaffold-test-scripts
 */

import javascript
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "scaffold-test-scripts")
select subject, message, contributor
