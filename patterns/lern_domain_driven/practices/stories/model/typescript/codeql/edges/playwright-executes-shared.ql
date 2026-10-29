/**
 * @name playwright-executes-shared
 * @kind problem
 * @id cdd/lern/stories/edges/playwright-executes-shared
 */

import javascript
import lern

from CallExpr specCall, CallExpr shared, string name, string file
where
  specFile(specCall.getFile(), "PlaywrightSpec") and
  specExecutes(specCall, shared) and
  sharedStoryCall(shared, name, file)
select specNodeId(specCall.getFile()), storySharedId(file, name), "executes", 5, "relationship"
