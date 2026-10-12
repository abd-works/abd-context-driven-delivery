/**
 * @name module-used-by-epics
 * @kind problem
 * @id cdd/stories/edges/module-used-by-epics
 */

import javascript
import stories

from string folder, string prefix, string mod, string parent, string child
where
  epicUsesModule(folder, prefix, mod) and
  parent = moduleNodeId(prefix, mod) and
  child = epicId(folder)
select parent, child, "usedBy", 9, "relationship" order by parent, child
