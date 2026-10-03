/**
 * @name limit-operation-parameters
 * @practice clean_engineering
 * @fidelity model
 * @node operation
 * @id clean_engineering/model/limit-operation-parameters
 * @problem.severity warning
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "limit-operation-parameters")
select subject, message, contributor
