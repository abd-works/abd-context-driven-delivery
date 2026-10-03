/**
 * @name Practice graph calls
 * @kind problem
 * @id cdd/practice-graph/calls
 */

import javascript
import subject_filter
import model

from Function caller, string calleeOwner, string calleeName, string calleeModule, string callerModule
where
  exists(graphOwnerName(caller)) and
  inSubject(caller) and
  callerModule = caller.getEnclosingModule().getName() and
  (
    exists(Function callee |
      directCall(caller, callee) and
      exists(graphOwnerName(callee)) and
      inSubject(callee) and
      calleeOwner = graphOwnerName(callee) and
      calleeName = callee.getName() and
      calleeModule = callee.getEnclosingModule().getName()
    )
    or
    exists(Attribute attr, Name receiver |
      attr.getScope() = caller and
      not exists(Call call | call.getFunc() = attr) and
      receiver = attr.getObject() and
      calleeName = attr.getName() and
      calleeModule = callerModule and
      (
        receiver.getId() = "self" and calleeOwner = graphOwnerName(caller)
        or
        receiver.getId() != "self" and
        receiver.getId() != "cls" and
        calleeOwner = receiver.getId()
      )
    )
  )
select graphOwnerName(caller), caller.getName(), calleeOwner, calleeName, calleeModule, callerModule
