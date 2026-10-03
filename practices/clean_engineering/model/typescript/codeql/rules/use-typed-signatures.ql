/**
 * @name use-typed-signatures
 * @practice clean_engineering
 * @fidelity modules
 * @node class
 * @id clean_engineering/modules/use-typed-signatures
 */

import javascript
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "use-typed-signatures")
select subject, message, contributor
