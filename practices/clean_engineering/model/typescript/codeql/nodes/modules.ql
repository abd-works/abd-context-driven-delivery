/**
 * @name modules
 * @kind problem
 * @id cdd/ce/nodes/modules
 */

import javascript
import ce

from string mod
where subjectModule(mod)
select moduleId(mod), mod, "Module", "clean_engineering", modulePath(mod), 1, 1, "discovery"
