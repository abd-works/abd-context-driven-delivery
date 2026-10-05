/**
 * @name modules
 * @kind problem
 * @id cdd/ce/nodes/modules
 */

import javascript
import clean_engineering.ce

from string mod
where subjectModule(mod)
select moduleId(mod), mod, "Module", "clean_engineering", "src/" + mod, 1, 1, "discovery"
