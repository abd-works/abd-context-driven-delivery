/**
 * @name examples
 * @kind problem
 * @id cdd/stories/nodes/examples
 */

import javascript
import stories.stories

from ExportNamedDeclaration decl, VarDecl exported, string file, string name
where
  exampleFile(decl.getFile()) and
  exported = decl.getADecl() and
  name = exported.getName() and
  not name.matches("seed%") and
  file = slash(decl.getFile().getRelativePath())
select exampleId(file, name), name, "Example", "stories", file, exported.getLocation().getStartLine(),
  exported.getLocation().getEndLine(), exampleReturnClass(exported.getParent()), "implementation"
