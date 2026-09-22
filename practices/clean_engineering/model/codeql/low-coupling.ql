/**
 * @name low-coupling
 * @kind problem
 * @id cdd/practice-graph/low-coupling
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function f, Attribute attr
where inSubject(f) and privateAttributeRead(f, attr)
select f,
  "Operation '" + f.getName() + "' reaches past a seam via '" + attr.getName() + "'.", attr
