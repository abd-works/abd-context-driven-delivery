/**
 * @name Practice graph calls
 * @kind problem
 * @id cdd/practice-graph/calls
 */

import python
import subject_filter
import model

from Function caller, Function callee
where
  exists(graphOwnerName(caller)) and
  exists(graphOwnerName(callee)) and
  inSubject(caller) and
  inSubject(callee) and
  directCall(caller, callee)
select graphOwnerName(caller), caller.getName(), graphOwnerName(callee), callee.getName(),
  callee.getEnclosingModule().getName(), caller.getEnclosingModule().getName()
