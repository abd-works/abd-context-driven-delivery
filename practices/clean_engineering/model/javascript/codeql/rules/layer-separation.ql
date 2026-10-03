/**
 * @name layer-separation
 * @practice clean_engineering
 * @fidelity modules
 * @node module
 * @id clean_engineering/modules/layer-separation
 */

import javascript
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "layer-separation")
select subject, message, contributor
