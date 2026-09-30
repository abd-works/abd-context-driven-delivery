/**
 * @name Practice graph properties
 * @kind problem
 * @id cdd/practice-graph/properties-javascript
 */

import javascript

string typeName(FieldDefinition field) { result = "" }

from FieldDefinition field
where exists(field.getDeclaringType().getName()) and exists(field.getName())
select field.getDeclaringType().getName(), field.getName(), field.getFile().getBaseName(),
  field.getLocation().getStartLine(),
  field.getFile().getRelativePath(),
  field.getLocation().getEndLine(),
  typeName(field)
