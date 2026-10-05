/**
 * @name Practice graph relative
 * @kind problem
 * @id cdd/practice-graph/relative
 */

import python
import subject_filter
import model
import members

from Class cls, AnnAssign assign, string name, string hint
where
  inSubject(assign) and
  assign.getScope() = cls and
  name = assign.getTarget().(Name).getId() and
  hint = assign.getAnnotation().toString() and
  isRelativeHint(hint)
select cls.getName(), name, assign.getLocation().getStartLine(), "true",
  assign.getLocation().getFile().getRelativePath()
