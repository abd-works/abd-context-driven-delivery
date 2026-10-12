/**
 * @name lern playwright spec
 * @kind problem
 * @id cdd/lern/stories/playwright-spec
 */

import javascript
import model

from File f, string id, string name, string file, int start, int end
where
  playwrightSpecFile(f) and
  file = slash(f.getRelativePath()) and
  name = f.getBaseName() and
  start = f.getLocation().getStartLine() and
  end = f.getLocation().getEndLine() and
  id = lernStoryNodeId(f, "PlaywrightSpec")
select id, name, "PlaywrightSpec", "stories", file, start, end, "implementation"
