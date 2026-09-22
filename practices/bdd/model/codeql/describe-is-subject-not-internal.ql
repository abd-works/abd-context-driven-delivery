/**
 * @name describe-is-subject-not-internal
 * @kind problem
 * @id cdd/practice-graph/describe-is-subject-not-internal
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Call call, string label
where
  inSubject(call) and
  internalDescribe(call) and
  label = call.getArg(0).(StringLiteral).getText()
select call, "Describe names internal type '" + label + "' instead of a domain subject.", call
