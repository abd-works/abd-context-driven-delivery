/**
 * @name examples
 * @kind problem
 * @id cdd/stories/nodes/examples
 */

import javascript
import stories

from ExportNamedDeclaration decl, string file, string name, int start, int end
where
  exampleExport(decl, name, start, end) and
  file = slash(decl.getFile().getRelativePath())
select exampleId(file, name), name, "Example", "stories", file, start, end, "implementation"
