/**
 * @name class-aggregation-classes
 * @kind problem
 * @id cdd/ce/edges/class-aggregation-classes
 */

import javascript
import ce

from ClassDefinition fromCls, ClassDefinition toCls, FieldDefinition field
where
  domainClass(fromCls) and
  domainClass(toCls) and
  fromCls != toCls and
  field.getDeclaringType() = fromCls and
  exists(Comment comment |
    comment.getLocation().getFile() = field.getLocation().getFile() and
    comment.getLocation().getEndLine() = field.getLocation().getStartLine() - 1 and
    comment.toString().toLowerCase().matches("%<<aggregation>>%")
  ) and
  hintNames(field.getTypeAnnotation().toString(), toCls.getName())
select classId(fromCls), classId(toCls), "aggregation", 12, "relationship"
