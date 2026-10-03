/**
 * @name prefer-instance-operations
 * @practice clean_engineering
 * @fidelity code
 * @node operation
 * @id clean_engineering/code/prefer-instance-operations
 * @problem.severity warning
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "prefer-instance-operations")
select subject, message, contributor
