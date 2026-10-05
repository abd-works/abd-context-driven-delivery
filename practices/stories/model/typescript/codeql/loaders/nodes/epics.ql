/**
 * @name epics
 * @kind problem
 * @id cdd/stories/nodes/epics
 */

import javascript
import stories

from File file, string folder
where
  storyFile(file) and
  folder = epicFolder(file)
select epicId(folder), epicName(folder), "Epic", "stories", folder, 1, 1
