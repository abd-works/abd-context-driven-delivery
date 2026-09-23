/**
 * @name Practice graph calls
 * @kind problem
 * @id cdd/practice-graph/calls
 */

import python
import subject_filter
import model

predicate namesCallee(Call call, Function callee) {
  call.getFunc().(Attribute).getName() = callee.getName()
  or
  call.getFunc().(Name).getId() = callee.getName()
}

predicate directCall(Function caller, Function callee) {
  inSubject(caller) and
  inSubject(callee) and
  exists(Call call | call.getScope() = caller and namesCallee(call, callee)) and
  caller != callee
}

from Function caller, Function callee
where
  exists(graphOwnerName(caller)) and
  exists(graphOwnerName(callee)) and
  directCall(caller, callee)
select graphOwnerName(caller), caller.getName(), graphOwnerName(callee), callee.getName(),
  callee.getEnclosingModule().getName(), caller.getEnclosingModule().getName()
