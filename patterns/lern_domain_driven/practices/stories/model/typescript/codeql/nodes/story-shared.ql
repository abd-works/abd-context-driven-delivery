/**
 * @name shared stories
 * @kind problem
 * @id cdd/lern/stories/nodes/story-shared
 */

import javascript
import lern

from CallExpr call, string name, string file
where sharedStoryCall(call, name, file)
select storySharedId(file, name), name, "StoryShared", "stories", file, call.getLocation().getStartLine(),
  call.getLocation().getEndLine(), "discovery"
