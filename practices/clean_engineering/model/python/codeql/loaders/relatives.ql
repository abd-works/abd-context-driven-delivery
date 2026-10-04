/**
 * @name Practice graph relatives
 * @kind problem
 * @id cdd/practice-graph/relatives
 */

import python
import subject_filter
import members

from AnnAssign assign, Class cls, string name, string hint
where
  inSubject(assign) and
  assign.getScope() = cls and
  name = assign.getTarget().(Name).getId() and
  (
    hint = assign.getAnnotation().toString()
    or
    not exists(assign.getAnnotation()) and hint = ""
  ) and
  isRelativeHint(hint)
select cls.getName(), name, assign.getLocation().getFile().getShortName(),
  assign.getLocation().getStartLine(),
  assign.getLocation().getFile().getRelativePath(),
  assign.getLocation().getEndLine(),
  hint
