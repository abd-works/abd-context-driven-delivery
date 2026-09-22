/**
 * @name provide-meaningful-context
 * @kind problem
 * @id cdd/practice-graph/provide-meaningful-context
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function f, Parameter p
where inSubject(f) and numberedParameter(f, p)
select f,
  "Operation '" + f.getName() + "' numbers parameter '" + p.getName() + "'.", p
