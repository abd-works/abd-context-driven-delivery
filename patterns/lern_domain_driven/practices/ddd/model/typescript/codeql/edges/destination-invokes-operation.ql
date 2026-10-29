/**
 * @name destination-invokes-operation
 * @kind problem
 * @id cdd/lern/ddd/edges/destination-invokes-operation
 */

import javascript
import lern

from MethodCallExpr destination, MethodCallExpr call, MethodDefinition method, string slug
where
  destinationCall(destination, _, _) and
  routeFile(destination.getFile(), slug) and
  callUnder(destination, call) and
  call.getCalleeName() = method.getName() and
  (
    rootOperation(slug, method) or
    repositoryVerb(slug, method)
  )
select destinationId(destination), operationNodeId(method), "invokes", 5, "relationship"
