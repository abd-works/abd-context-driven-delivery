/**
 * @name prefer-class-operations
 * @kind problem
 * @id cdd/practice-graph/prefer-class-operations
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function f, Class cls
where inSubject(f) and calledOnlyFrom(f, cls)
select f,
  "Function '" + f.getName() + "' is only called from '" + cls.getName() + "'.", cls
