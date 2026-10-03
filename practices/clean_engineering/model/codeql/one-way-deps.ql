/**
 * @name one-way-deps
 * @practice clean_engineering
 * @fidelity modules
 * @node module
 * @id clean_engineering/modules/one-way-deps
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "one-way-deps")
select subject, message, contributor
