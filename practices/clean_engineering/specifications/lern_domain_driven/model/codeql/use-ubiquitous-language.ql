/**
 * @name use-ubiquitous-language
 * @kind problem
 * @id cdd/practice-graph/use-ubiquitous-language
 * @problem.severity warning
 */

import javascript
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "use-ubiquitous-language")
select subject, message, contributor
