/**
 * @name put-logic-on-the-owning-resource
 * @practice clean_engineering
 * @fidelity model
 * @node class
 * @id clean_engineering/model/put-logic-on-the-owning-resource
 */

import javascript
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "put-logic-on-the-owning-resource")
select subject, message, contributor
