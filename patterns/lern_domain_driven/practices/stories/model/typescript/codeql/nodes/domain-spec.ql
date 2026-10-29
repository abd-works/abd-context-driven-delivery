/**
 * @name domain specs
 * @kind problem
 * @id cdd/lern/stories/nodes/domain-spec
 */

import javascript
import lern

from File file
where specFile(file, "DomainSpec")
select specNodeId(file), file.getBaseName(), "DomainSpec", "stories", fileSlash(file.getRelativePath()), 1, 1,
  "discovery"
