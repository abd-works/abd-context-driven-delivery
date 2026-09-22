/**
 * @name avoid-vague-parameter-names
 * @kind problem
 * @id cdd/practice-graph/avoid-vague-parameter-names
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function f, Parameter p
where
  inSubject(f) and
  domainParameter(f, p) and
  (p.getName() = "data" or p.getName() = "options" or p.getName() = "info")
select f,
  "Operation '" + f.getName() + "' names a parameter '" + p.getName() + "'.", p
