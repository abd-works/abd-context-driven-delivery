/**
 * @name Practice graph properties
 * @kind problem
 * @id cdd/practice-graph/properties
 */

import python
import subject_filter
import model

predicate moduleLevelBinding(AstNode assign, string name) {
  assign.getScope() instanceof Module and
  (
    name = assign.(AnnAssign).getTarget().(Name).getId()
    or
    name = assign.(Assign).getATarget().(Name).getId()
  ) and
  not name.matches("\\_%")
}

from AstNode assign, string name, string owner
where
  inSubject(assign) and
  (
    exists(Class cls |
      assign.getScope() = cls and
      name = assign.(AnnAssign).getTarget().(Name).getId() and
      not name.matches("\\_%") and
      owner = cls.getName()
    )
    or
    (
      moduleLevelBinding(assign, name) and
      owner = normalizedPath(assign.getLocation().getFile())
    )
  )
select owner, name, assign.getLocation().getFile().getShortName(),
  assign.getLocation().getStartLine(),
  assign.getLocation().getFile().getRelativePath(),
  assign.getLocation().getEndLine()
