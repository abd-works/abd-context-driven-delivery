/**
 * @name Practice graph properties
 * @kind problem
 * @id cdd/practice-graph/properties
 */

import python
import subject_filter

from Class cls, AnnAssign assign, string name
where
  inSubject(cls) and
  assign.getScope() = cls and
  name = assign.getTarget().(Name).getId() and
  not name.matches("\\_%")
select cls.getName(), name, cls.getEnclosingModule().getName(),
  assign.getLocation().getStartLine()
