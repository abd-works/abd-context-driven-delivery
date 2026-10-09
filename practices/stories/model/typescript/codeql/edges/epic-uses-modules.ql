/**
 * @name epic-uses-modules
 * @kind problem
 * @id cdd/stories/edges/epic-uses-modules
 */

import javascript
import stories

from string folder, string prefix, string mod
where epicUsesModule(folder, prefix, mod)
select epicId(folder), moduleNodeId(prefix, mod), "uses", 9, "relationship"
  order by folder, prefix, mod
