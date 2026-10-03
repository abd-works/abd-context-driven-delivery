/**
 * @name deep-module
 * @practice clean_engineering
 * @fidelity modules
 * @node module
 * @id clean_engineering/modules/deep-module
 */

import javascript
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "deep-module")
select subject, message, contributor
