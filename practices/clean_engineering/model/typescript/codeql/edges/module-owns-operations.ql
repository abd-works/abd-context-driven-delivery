/**
 * @name module-owns-operations
 * @kind problem
 * @id cdd/ce/edges/module-owns-operations
 */

import javascript
import ce

from string parent, string child, Function func
where
  bareFunction(func) and
  parent = moduleId(moduleOfFile(slash(func.getFile().getRelativePath()))) and
  child = bareFunctionId(func)
select parent, child, "owns", 2, "direct" order by parent, child
