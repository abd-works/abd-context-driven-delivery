/**
 * @name example-retrieved-using-properties
 * @kind problem
 * @id cdd/stories/edges/example-retrieved-using-properties
 */

import javascript
import stories

from string file, string name, PropAccess access, FieldDefinition field, string parent, string child
where
  access.getEnclosingFunction*() = exampleFactory(file, name) and
  not exists(MethodCallExpr call | call.getCallee().stripParens() = access) and
  field.getName() = access.getPropertyName() and
  field.getDeclaringType().getName() = exampleReturnClassName(file, name) and
  parent = exampleId(file, name) and
  child = propertyNodeId(field)
select parent, child, "retrievedUsing", 7, "relationship"
