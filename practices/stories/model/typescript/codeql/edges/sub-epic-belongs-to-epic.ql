/**
 * @name sub-epic-belongs-to-epic
 * @kind problem
 * @id cdd/stories/edges/sub-epic-belongs-to-epic
 */

import javascript
import stories

from File file, string folder, string parent, string child
where
  storyFile(file) and
  folder = subEpicFolder(file) and
  parent = subEpicId(folder) and
  child = epicId(epicFolder(file))
select parent, child, "belongsTo", 4, "relationship"
