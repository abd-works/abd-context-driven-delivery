/**
 * @name Practice graph operations
 * @kind problem
 * @id cdd/practice-graph/operations
 */

import python
import subject_filter

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

from Class cls, Function method
where inSubject(cls) and method = cls.getAMethod()
select cls.getName(), method.getName(), returnedName(method),
  method.getLocation().getStartLine()
