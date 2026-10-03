/**
 * @name describe-is-subject-not-internal
 * @practice bdd
 * @fidelity
 * @node describe
 * @id bdd/describe-is-subject-not-internal
 */

import javascript
import subject_filter
import model

from CallExpr call, string label
where
  inSubject(call) and
  internalDescribe(call) and
  label = call.getArgument(0).(StringLiteral).getValue()
select call, "Describe names internal type '" + label + "' instead of a domain subject.", call
