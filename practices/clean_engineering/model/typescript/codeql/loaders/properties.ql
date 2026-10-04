/**
 * @name Practice graph properties
 * @kind problem
 * @id cdd/practice-graph/properties
 */

import javascript
import subject_filter
import members

from FieldDefinition field, string name, string hint
where
  classField(field) and
  name = field.getName() and
  hint = fieldHint(field) and
  not isRelativeHint(hint)
select field.getDeclaringType().getName(), name, field.getFile().getBaseName(),
  field.getLocation().getStartLine(),
  field.getFile().getRelativePath(),
  field.getLocation().getEndLine(),
  hint
union
from MethodDefinition accessor, string name, string hint
where
  classAccessor(accessor) and
  name = accessor.getName() and
  hint = accessorHint(accessor) and
  not isRelativeHint(hint)
select accessor.getDeclaringType().getName(), name, accessor.getFile().getBaseName(),
  accessor.getLocation().getStartLine(),
  accessor.getFile().getRelativePath(),
  accessor.getLocation().getEndLine(),
  hint
