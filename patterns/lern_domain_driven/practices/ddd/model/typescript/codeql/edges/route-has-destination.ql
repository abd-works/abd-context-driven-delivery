/**
 * @name route-has-destination
 * @kind problem
 * @id cdd/lern/ddd/edges/route-has-destination
 */

import javascript
import lern

from MethodCallExpr call, File file
where destinationCall(call, _, _) and file = call.getFile()
select routeId(file), destinationId(call), "has", 2, "direct"
