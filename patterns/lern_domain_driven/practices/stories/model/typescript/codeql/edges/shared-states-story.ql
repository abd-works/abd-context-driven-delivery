/**
 * @name shared-states-story
 * @kind problem
 * @id cdd/lern/stories/edges/shared-states-story
 */

import javascript
import lern

from CallExpr call, string name, string file
where sharedStoryCall(call, name, file)
select storySharedId(file, name), storyId(file, name), "states", 5, "relationship"
