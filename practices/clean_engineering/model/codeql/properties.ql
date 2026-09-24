/**
 * @name Practice graph properties
 * @kind problem
 * @id cdd/practice-graph/properties
 */

import python
import subject_filter
import model

from AnnAssign assign, Class cls, string name
where
  inSubject(assign) and
  assign.getScope() = cls and
  name = assign.getTarget().(Name).getId() and
  not name.matches("\\_%")
select cls.getName(), name, assign.getLocation().getFile().getShortName(),
  assign.getLocation().getStartLine(),
  assign.getLocation().getFile().getRelativePath(),
  assign.getLocation().getEndLine()
