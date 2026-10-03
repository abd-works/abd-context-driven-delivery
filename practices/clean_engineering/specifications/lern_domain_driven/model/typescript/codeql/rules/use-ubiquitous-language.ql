/**
 * @name use-ubiquitous-language
 * @practice lern_domain_driven
 * @fidelity code
 * @node class
 * @id lern_domain_driven/code/use-ubiquitous-language
 */

import javascript
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "use-ubiquitous-language")
select subject, message, contributor
