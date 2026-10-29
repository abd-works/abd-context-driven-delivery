/**
 * @name server specs
 * @kind problem
 * @id cdd/lern/stories/nodes/server-spec
 */

import javascript
import lern

from File file
where specFile(file, "ServerSpec")
select specNodeId(file), file.getBaseName(), "ServerSpec", "stories", fileSlash(file.getRelativePath()), 1, 1,
  "discovery"
