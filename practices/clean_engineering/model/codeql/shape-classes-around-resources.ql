/**
 * @name shape-classes-around-resources
 * @kind problem
 * @id cdd/practice-graph/shape-classes-around-resources
 * @problem.severity warning
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "shape-classes-around-resources")
select subject, message, contributor
