/**
 * @name ddd has-identity
 * @kind problem
 * @id cdd/ddd/has-identity
 */

import javascript
import ddd

from ClassDefinition cls, FieldDefinition field, string parent, string child, string file
where
  (dddClass(cls, "EntityRoot", parent, _, file, _, _) or dddClass(cls, "Entity", parent, _, file, _, _)) and
  field.getDeclaringType() = cls and
  (
    field.getName() = "id" or
    field.getName() = "identity" or
    fieldComment(field, "identifier")
  ) and
  child =
    "ddd:Property:" + file + ":" + field.getName() + ":" + cls.getName()
select parent, child, "hasIdentity", 3, "direct"
