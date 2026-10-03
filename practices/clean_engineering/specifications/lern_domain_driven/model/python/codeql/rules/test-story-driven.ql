/**
 * @name test-story-driven
 * @practice lern_domain_driven
 * @fidelity code
 * @node module
 * @id lern_domain_driven/code/test-story-driven
 * @connection stories.stories
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "test-story-driven")
select subject, message, contributor
