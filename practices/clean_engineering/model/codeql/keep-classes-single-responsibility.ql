/**
 * @name keep-classes-single-responsibility
 * @practice clean_engineering
 * @fidelity model
 * @node class
 * @id clean_engineering/model/keep-classes-single-responsibility
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "keep-classes-single-responsibility")
select subject, message, contributor
