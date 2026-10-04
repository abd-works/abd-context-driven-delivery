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
  not name.matches("\\_%") and
  not exists(ObjectExpr object |
    field.getLocation().getFile() = object.getLocation().getFile() and
    field.getLocation().getStartLine() >= object.getLocation().getStartLine() and
    field.getLocation().getEndLine() <= object.getLocation().getEndLine() and
    not object = field.getInit()
  )
select field.getDeclaringType().getName(), name, field.getFile().getBaseName(),
  field.getLocation().getStartLine(),
  field.getFile().getRelativePath(),
  field.getLocation().getEndLine(),
  ""
