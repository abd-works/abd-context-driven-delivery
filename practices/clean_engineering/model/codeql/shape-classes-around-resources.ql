/**
 * @name shape-classes-around-resources
 * @practice clean_engineering
 * @fidelity model
 * @node class
 * @id clean_engineering/model/shape-classes-around-resources
 * @problem.severity warning
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "shape-classes-around-resources")

select subject, message, contributor
