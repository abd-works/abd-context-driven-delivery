/**
 * @name class-belongs-to-module
 * @kind problem
 * @id cdd/ce/edges/class-belongs-to-module
 */

import javascript
import ce

from ClassDefinition cls
where domainClass(cls)
select classId(cls), moduleId(moduleOf(cls)), "belongsTo", 4, "relationship"
