/**
 * @name epic-uses-modules
 * @kind problem
 * @id cdd/stories/edges/epic-uses-modules
 */

import javascript
import stories

from string folder, string prefix, string mod, string parent, string child
where
  epicUsesModule(folder, prefix, mod) and
  parent = epicId(folder) and
  child = moduleNodeId(prefix, mod)
select parent, child, "uses", 9, "relationship" order by parent, child
