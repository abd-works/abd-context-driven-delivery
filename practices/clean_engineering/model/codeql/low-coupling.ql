/**
 * @name low-coupling
 * @practice clean_engineering
 * @fidelity modules
 * @node module
 * @id clean_engineering/modules/low-coupling
 * @problem.severity warning
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "low-coupling")
select subject, message, contributor
