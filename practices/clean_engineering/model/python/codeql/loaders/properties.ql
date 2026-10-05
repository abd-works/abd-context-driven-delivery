/**
 * @name Practice graph properties
 * @kind problem
 * @id cdd/practice-graph/properties
 */

import python
import subject_filter
import model
import members

from string className, string name, string base, int start, string path, int end, string hint
where
  exists(AnnAssign assign, Class cls |
    inSubject(assign) and
    assign.getScope() = cls and
    name = assign.getTarget().(Name).getId() and
    className = cls.getName() and
    base = assign.getLocation().getFile().getShortName() and
    start = assign.getLocation().getStartLine() and
    path = assign.getLocation().getFile().getRelativePath() and
    end = assign.getLocation().getEndLine() and
    (
      hint = assign.getAnnotation().toString()
      or
      not exists(assign.getAnnotation()) and hint = ""
    ) and
    not isRelativeHint(hint)
  )
  or
  exists(Function method, Class cls |
    inSubject(method) and
    decoratorNamed(method, "property") and
    cls = method.getScope() and
    className = cls.getName() and
    name = method.getName() and
    base = method.getLocation().getFile().getShortName() and
    start = method.getLocation().getStartLine() and
    path = method.getLocation().getFile().getRelativePath() and
    end = method.getLocation().getEndLine() and
    hint = ""
  )
select className, name, base, start, path, end, hint
