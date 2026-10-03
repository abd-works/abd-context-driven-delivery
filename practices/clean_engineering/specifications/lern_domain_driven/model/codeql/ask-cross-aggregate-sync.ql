/**
 * @name ask-cross-aggregate-sync
 * @practice lern_domain_driven
 * @fidelity code
 * @node stories
 * @id lern_domain_driven/code/ask-cross-aggregate-sync
 * @problem.severity warning
 * @connection stories.stories
 */

import javascript
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "ask-cross-aggregate-sync")
select subject, message, contributor
