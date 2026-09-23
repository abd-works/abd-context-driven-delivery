/**
 * @name Practice graph operations
 * @kind problem
 * @id cdd/practice-graph/operations
 */

import python
import subject_filter
import source_span
import model

string returnedName(Function method) {
  exists(Return ret, Name name |
    ret.getScope() = method and
    name = ret.getValue() and
    result = name.getId()
  )
  or
  exists(Return ret, Call call |
    ret.getScope() = method and
    call = ret.getValue() and
    result = call.getFunc().(Name).getId()
  )
  or
  not exists(Return ret | ret.getScope() = method and exists(ret.getValue())) and
  result = ""
}

from Function method
where inSubject(method) and exists(graphOwnerName(method))
select graphOwnerName(method), method.getName(), returnedName(method),
  sourceStart(method),
  method.getLocation().getFile().getRelativePath(),
  sourceEnd(method)
