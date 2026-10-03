/**
 * @name keep-operations-small-focused
 * @practice clean_engineering
 * @fidelity code
 * @node operation
 * @id clean_engineering/code/keep-operations-small-focused
 * @problem.severity warning
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "keep-operations-small-focused")
select subject, message, contributor
