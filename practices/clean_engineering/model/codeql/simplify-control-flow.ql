/**
 * @name simplify-control-flow
 * @practice clean_engineering
 * @fidelity code
 * @node operation
 * @id clean_engineering/code/simplify-control-flow
 * @problem.severity warning
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "simplify-control-flow")
select subject, message, contributor
