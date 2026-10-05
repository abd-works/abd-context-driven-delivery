/**
 * @name Practice graph invokes
 * @kind problem
 * @id cdd/practice-graph/invokes
 */

import python
import subject_filter
import model

from Function caller, string calleeOwner, string calleeName
where
  exists(graphOwnerName(caller)) and
  inSubject(caller) and
  not accessorOperation(caller) and
  not decoratorNamed(caller, "property") and
  exists(Function callee |
    directCall(caller, callee) and
    exists(graphOwnerName(callee)) and
    inSubject(callee) and
    calleeOwner = graphOwnerName(callee) and
    calleeName = callee.getName()
  )
select graphOwnerName(caller) + "." + caller.getName(), calleeOwner + "." + calleeName,
  caller.getLocation().getStartLine(), "true",
  caller.getLocation().getFile().getRelativePath()
