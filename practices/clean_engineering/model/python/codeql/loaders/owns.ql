/**
 * @name Practice graph owns
 * @kind problem
 * @id cdd/practice-graph/owns
 */

import python
import subject_filter
import model
import members

from string parent, string child, int seq, string immediate, string file
where
  exists(Class cls, Function method |
    inSubject(method) and
    ownerClass(method, cls) and
    not accessorOperation(method) and
    not decoratorNamed(method, "property") and
    parent = cls.getName() and
    child = method.getName() and
    seq = method.getLocation().getStartLine() and
    immediate = "true" and
    file = method.getLocation().getFile().getRelativePath()
  )
  or
  exists(Class cls, AnnAssign assign, string hint |
    inSubject(assign) and
    assign.getScope() = cls and
    child = assign.getTarget().(Name).getId() and
    parent = cls.getName() and
    seq = assign.getLocation().getStartLine() and
    file = assign.getLocation().getFile().getRelativePath() and
    (
      hint = assign.getAnnotation().toString()
      or
      not exists(assign.getAnnotation()) and hint = ""
    ) and
    (if isRelativeHint(hint) then immediate = "true" else immediate = "false")
  )
  or
  exists(Function method, Class cls |
    inSubject(method) and
    decoratorNamed(method, "property") and
    cls = method.getScope() and
    parent = cls.getName() and
    child = method.getName() and
    seq = method.getLocation().getStartLine() and
    immediate = "true" and
    file = method.getLocation().getFile().getRelativePath()
  )
select parent, child, seq, immediate, file
