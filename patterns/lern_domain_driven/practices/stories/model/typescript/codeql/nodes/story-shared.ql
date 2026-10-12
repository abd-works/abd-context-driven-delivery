/**
 * @name lern story shared
 * @kind problem
 * @id cdd/lern/stories/story-shared
 */

import javascript
import model

from File f, string id, string name, string file, int start, int end
where
  storySharedFile(f) and
  file = slash(f.getRelativePath()) and
  name = f.getBaseName() and
  start = f.getLocation().getStartLine() and
  end = f.getLocation().getEndLine() and
  id = lernStoryNodeId(f, "StoryShared")
select id, name, "StoryShared", "stories", file, start, end, "specification"
