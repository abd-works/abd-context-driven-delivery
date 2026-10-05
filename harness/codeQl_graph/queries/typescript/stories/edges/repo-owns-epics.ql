/**
 * @name repo-owns-epics
 * @kind problem
 * @id cdd/stories/edges/repo-owns-epics
 */

import javascript
import stories.stories

from File file, string folder, string parent, string child
where
  storyFile(file) and
  folder = epicFolder(file) and
  parent = storiesPracticeId() and
  child = epicId(folder)
select parent, child, "owns", 1, "direct" order by parent, child
