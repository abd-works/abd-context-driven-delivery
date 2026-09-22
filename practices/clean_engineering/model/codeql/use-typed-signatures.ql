/**
 * @name use-typed-signatures
 * @kind problem
 * @id cdd/practice-graph/use-typed-signatures
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function f, Parameter p
where inSubject(f) and untypedPublicParameter(f, p)
select f,
  "Operation '" + f.getName() + "' leaves parameter '" + p.getName() + "' untyped.", p
