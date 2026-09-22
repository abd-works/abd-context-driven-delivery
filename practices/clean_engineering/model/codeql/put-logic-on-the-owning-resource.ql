/**
 * @name put-logic-on-the-owning-resource
 * @kind problem
 * @id cdd/practice-graph/put-logic-on-the-owning-resource
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function f, Parameter p
where inSubject(f) and envies(f, p)
select f,
  "Operation '" + f.getName() + "' works through parameter '" + p.getName() +
    "' instead of that object.", p
