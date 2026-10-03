/**
 * @name avoid-vague-parameter-names
 * @practice clean_engineering
 * @fidelity model
 * @node parameter
 * @id clean_engineering/model/avoid-vague-parameter-names
 * @problem.severity warning
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "avoid-vague-parameter-names")
select subject, message, contributor
