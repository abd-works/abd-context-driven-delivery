/**
 * @name belongs-to
 * @kind problem
 * @id cdd/ce/edges/belongs-to
 */

import javascript
import ce

from ClassDefinition cls
where domainClass(cls)
select classId(cls), moduleId(moduleOf(cls)), "belongsTo", 4, "relationship"
