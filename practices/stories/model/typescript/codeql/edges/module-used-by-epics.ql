/**
 * @name module-used-by-epics
 * @kind problem
 * @id cdd/stories/edges/module-used-by-epics
 */

import javascript
import stories

from string folder, string prefix, string mod
where epicUsesModule(folder, prefix, mod)
select moduleNodeId(prefix, mod), epicId(folder), "usedBy", 9, "relationship"
  order by prefix, mod, folder
