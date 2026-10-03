/**
 * @name consistent-view-naming
 * @practice lern_domain_driven
 * @fidelity code
 * @node class
 * @id lern_domain_driven/code/consistent-view-naming
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "consistent-view-naming")
select subject, message, contributor
