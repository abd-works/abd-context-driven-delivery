/**
 * @name entity-associates-entities
 * @kind problem
 * @id cdd/ddd/edges/entity-associates-entities
 */

import javascript
import ddd.ddd

from ClassDefinition fromCls, ClassDefinition toCls, string parent, string child, string toKind
where
  dddClass(fromCls, "Entity", parent, _, _, _, _) and
  dddClass(toCls, toKind, child, _, _, _, _) and
  fromCls != toCls and
  (toKind = "EntityRoot" or toKind = "Entity") and
  exists(FieldDefinition field |
    field.getDeclaringType() = fromCls and
    fieldComment(field, "foreign") and
    typeNames(field, toCls.getName())
  )
select parent, child, "associates", 6, "relationship"
