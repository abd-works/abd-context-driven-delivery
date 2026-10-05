/**
 * @name sub-epics
 * @kind problem
 * @id cdd/stories/nodes/sub-epics
 */

import javascript
import stories

from File file, string folder
where
  storyFile(file) and
  folder = subEpicFolder(file)
select subEpicId(folder), subEpicName(folder), "SubEpic", "stories", folder, 1, 1, "discovery"
