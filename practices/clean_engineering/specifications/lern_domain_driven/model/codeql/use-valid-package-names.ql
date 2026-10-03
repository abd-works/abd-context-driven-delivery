/**
 * @name use-valid-package-names
 * @practice lern_domain_driven
 * @fidelity code
 * @node module
 * @id lern_domain_driven/code/use-valid-package-names
 * @problem.severity warning
 */

import javascript
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "use-valid-package-names")
select subject, message, contributor
