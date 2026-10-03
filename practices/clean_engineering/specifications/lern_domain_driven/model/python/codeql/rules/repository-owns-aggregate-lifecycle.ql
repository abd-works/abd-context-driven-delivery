/**
 * @name repository-owns-aggregate-lifecycle
 * @practice lern_domain_driven
 * @fidelity code
 * @node class
 * @id lern_domain_driven/code/repository-owns-aggregate-lifecycle
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "repository-owns-aggregate-lifecycle")
select subject, message, contributor
