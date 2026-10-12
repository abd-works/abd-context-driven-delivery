/**
 * @name lern domain spec
 * @kind problem
 * @id cdd/lern/stories/domain-spec
 */

import javascript
import model

from File f, string id, string name, string file, int start, int end
where
  domainSpecFile(f) and
  file = slash(f.getRelativePath()) and
  name = f.getBaseName() and
  start = f.getLocation().getStartLine() and
  end = f.getLocation().getEndLine() and
  id = lernStoryNodeId(f, "DomainSpec")
select id, name, "DomainSpec", "stories", file, start, end, "implementation"
