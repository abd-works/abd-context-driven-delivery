/**
 * @name module-owns-classes
 * @kind problem
 * @id cdd/ce/edges/module-owns-classes
 */

import javascript
import ce

from ClassDefinition cls, string parent, string child
where
  domainClass(cls) and
  not exists(packageOfFile(classFile(cls))) and
  parent = moduleId(moduleOf(cls)) and
  child = classId(cls)
select parent, child, "owns", 2, "direct" order by parent, child
