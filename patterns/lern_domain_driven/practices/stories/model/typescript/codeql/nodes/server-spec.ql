/**
 * @name lern server spec
 * @kind problem
 * @id cdd/lern/stories/server-spec
 */

import javascript
import model

from File f, string id, string name, string file, int start, int end
where
  serverSpecFile(f) and
  file = slash(f.getRelativePath()) and
  name = f.getBaseName() and
  start = f.getLocation().getStartLine() and
  end = f.getLocation().getEndLine() and
  id = lernStoryNodeId(f, "ServerSpec")
select id, name, "ServerSpec", "stories", file, start, end, "implementation"
