/**
 * @name playwright specs
 * @kind problem
 * @id cdd/lern/stories/nodes/playwright-spec
 */

import javascript
import lern

from File file
where specFile(file, "PlaywrightSpec")
select specNodeId(file), file.getBaseName(), "PlaywrightSpec", "stories", fileSlash(file.getRelativePath()), 1, 1,
  "discovery"
