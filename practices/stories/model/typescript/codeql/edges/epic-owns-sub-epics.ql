/**
 * @name epic-owns-sub-epics
 * @kind problem
 * @id cdd/stories/edges/epic-owns-sub-epics
 */

import javascript
import stories

from File file, string folder, string parent, string child
where
  storyFile(file) and
  folder = subEpicFolder(file) and
  parent = epicId(epicFolder(file)) and
  child = subEpicId(folder)
select parent, child, "owns", 1, "direct" order by parent, child
