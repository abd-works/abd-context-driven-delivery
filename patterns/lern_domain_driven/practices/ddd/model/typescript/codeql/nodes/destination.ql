/**
 * @name destinations
 * @kind problem
 * @id cdd/lern/ddd/nodes/destination
 */

import javascript
import lern

from MethodCallExpr call, string http, string path
where destinationCall(call, http, path)
select destinationId(call), destinationName(http, path), "Destination", "ddd", fileOf(call),
  call.getLocation().getStartLine(), call.getLocation().getEndLine(), "implementation"
