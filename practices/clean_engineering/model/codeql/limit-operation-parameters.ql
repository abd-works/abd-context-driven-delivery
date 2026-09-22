/**
 * @name limit-operation-parameters
 * @kind problem
 * @id cdd/practice-graph/limit-operation-parameters
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function f
where inSubject(f) and tooManyParameters(f)
select f,
  "Operation '" + f.getName() + "' takes " + domainParameterCount(f).toString() +
    " parameters (prefer 0-2).", f
