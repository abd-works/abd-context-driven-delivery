/**
 * @name extensions-live-with-the-domain
 * @kind problem
 * @id cdd/practice-graph/extensions-live-with-the-domain
 * @problem.severity warning
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "extensions-live-with-the-domain")
select subject, message, contributor
