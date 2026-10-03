/**
 * @name Practice graph properties
 * @kind problem
 * @id cdd/practice-graph/properties
 */

import javascript
import subject_filter

from FieldDefinition field, string name
where
  inSubject(field) and
  name = field.getName() and
  not name.matches("\\_%")
select field.getDeclaringType().getName(), name, field.getFile().getBaseName(),
  field.getLocation().getStartLine(),
  field.getFile().getRelativePath(),
  field.getLocation().getEndLine(),
  ""
