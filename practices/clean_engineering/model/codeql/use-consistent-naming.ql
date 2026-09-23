/**
 * @name use-consistent-naming
 * @kind problem
 * @id cdd/practice-graph/use-consistent-naming
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Module m, Function f
where inSubject(f) and mixedNamingFunction(m, f)
select f,
  "Operation '" + f.getName() + "' mixes snake_case and camelCase in one module.", f
