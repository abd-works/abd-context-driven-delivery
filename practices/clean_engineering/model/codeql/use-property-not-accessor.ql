/**
 * @name use-property-not-accessor
 * @practice clean_engineering
 * @fidelity model
 * @node operation
 * @id clean_engineering/model/use-property-not-accessor
 * @problem.severity warning
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "use-property-not-accessor")
select subject, message, contributor
