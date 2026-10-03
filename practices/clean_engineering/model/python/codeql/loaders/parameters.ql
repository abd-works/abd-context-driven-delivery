/**
 * @name Practice graph parameters
 * @kind problem
 * @id cdd/practice-graph/parameters
 */

import python
import subject_filter
import model

from Function method, Parameter param
where
  inSubject(method) and
  exists(graphOwnerName(method)) and
  param = method.getAnArg() and
  param.getName() != "self" and
  param.getName() != "cls"
select graphOwnerName(method), method.getName(), param.getName(),
  param.getLocation().getStartLine(),
  param.getLocation().getFile().getRelativePath(),
  param.getLocation().getEndLine()
