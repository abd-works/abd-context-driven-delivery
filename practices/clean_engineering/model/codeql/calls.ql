/**
 * @name Practice graph calls
 * @kind problem
 * @id cdd/practice-graph/calls
 */

import python
import subject_filter

predicate ownerClass(Function method, Class cls) { method = cls.getAMethod() }

predicate directCall(Function caller, Function callee, Class calleeClass) {
  inSubject(caller) and
  inSubject(callee) and
  ownerClass(callee, calleeClass) and
  exists(Call call |
    call.getScope() = caller and
    call.getFunc().(Attribute).getName() = callee.getName()
  ) and
  caller != callee
}

from Class callerClass, Function caller, Class calleeClass, Function callee
where
  inSubject(callerClass) and
  ownerClass(caller, callerClass) and
  directCall(caller, callee, calleeClass)
select callerClass.getName(), caller.getName(), calleeClass.getName(), callee.getName(),
  calleeClass.getEnclosingModule().getName(), callerClass.getEnclosingModule().getName()
