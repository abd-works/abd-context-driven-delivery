/**
 * @name use-exceptions-properly
 * @practice clean_engineering
 * @fidelity code
 * @node operation
 * @id clean_engineering/code/use-exceptions-properly
 * @problem.severity warning
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "use-exceptions-properly")
select subject, message, contributor
