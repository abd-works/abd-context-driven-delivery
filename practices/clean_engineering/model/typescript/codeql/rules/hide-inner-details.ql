/**
 * @name hide-inner-details
 * @practice clean_engineering
 * @fidelity model
 * @node class
 * @id clean_engineering/model/hide-inner-details
 */

import javascript
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "hide-inner-details")
select subject, message, contributor
