/**
 * @name classes
 * @kind problem
 * @id cdd/ce/nodes/classes
 */

import javascript
import ce
import source_span

from ClassDefinition cls
where domainClass(cls)
select classId(cls), cls.getName(), "OoadClass", "clean_engineering", classFile(cls),
  sourceStart(cls), cls.getLocation().getEndLine(), moduleOf(cls), "implementation"
