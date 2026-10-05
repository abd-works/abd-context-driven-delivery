/**
 * @name ddd composition
 * @kind problem
 * @id cdd/ddd/composition
 */

import javascript
import ddd

from ClassDefinition fromCls, ClassDefinition toCls, string parent, string child
where
  dddClass(fromCls, _, parent, _, _, _, _) and
  dddClass(toCls, _, child, _, _, _, _) and
  fromCls != toCls and
  exists(FieldDefinition field |
    field.getDeclaringType() = fromCls and
    fieldComment(field, "<<composition>>") and
    typeNames(field, toCls.getName())
  )
select parent, child, "composition", 7, "relationship"
