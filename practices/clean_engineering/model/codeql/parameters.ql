/**
 * @name Practice graph parameters
 * @kind problem
 * @id cdd/practice-graph/parameters
 */

import python
import subject_filter

from Class cls, Function method, Parameter param
where
  inSubject(cls) and
  method = cls.getAMethod() and
  param = method.getAnArg() and
  param.getName() != "self"
select cls.getName(), method.getName(), param.getName(),
  param.getLocation().getStartLine()
