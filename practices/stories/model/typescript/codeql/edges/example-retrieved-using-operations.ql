/**
 * @name example-retrieved-using-operations
 * @kind problem
 * @id cdd/stories/edges/example-retrieved-using-operations
 */

import javascript
import stories
import members

from string file, string name, MethodCallExpr call, MethodDefinition callee, string parent, string child
where
  call.getEnclosingFunction*() = exampleFactory(file, name) and
  callee = resolvedMethod(call) and
  callee.getDeclaringType().getName() = exampleReturnClassName(file, name) and
  parent = exampleId(file, name) and
  child = operationNodeId(callee)
select parent, child, "retrievedUsing", 7, "relationship"
