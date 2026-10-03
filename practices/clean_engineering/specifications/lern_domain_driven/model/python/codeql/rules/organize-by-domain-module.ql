/**
 * @name organize-by-domain-module
 * @practice lern_domain_driven
 * @fidelity code
 * @node module
 * @id lern_domain_driven/code/organize-by-domain-module
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "organize-by-domain-module")
select subject, message, contributor
