/**
 * @name functions
 * @kind problem
 * @id cdd/ce/nodes/functions
 */

import javascript
import clean_engineering.ce
import source_span

from Function func
where bareFunction(func)
select bareFunctionId(func), func.getName(), "Operation", "clean_engineering",
  slash(func.getFile().getRelativePath()), sourceStart(func), func.getLocation().getEndLine(),
  moduleOfFile(slash(func.getFile().getRelativePath())), "implementation"
