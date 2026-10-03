/**
 * @name use-thorough-e2e-tests
 * @practice lern_domain_driven
 * @fidelity code
 * @node module
 * @id lern_domain_driven/code/use-thorough-e2e-tests
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "use-thorough-e2e-tests")
select subject, message, contributor
