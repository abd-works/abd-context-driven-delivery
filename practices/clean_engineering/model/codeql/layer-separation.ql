/**
 * @name layer-separation
 * @kind problem
 * @id cdd/practice-graph/layer-separation
 * @problem.severity warning
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "layer-separation")
select subject, message, contributor
