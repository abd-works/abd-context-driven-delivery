/**
 * @name demonstrated-through
 * @kind problem
 * @id cdd/stories/edges/demonstrated-through
 */

import javascript
import stories

from ExportNamedDeclaration decl, VarDecl exported, ClassDefinition cls, string file, string name
where
  exampleFile(decl.getFile()) and
  exported = decl.getADecl() and
  name = exported.getName() and
  not name.matches("seed%") and
  file = slash(decl.getFile().getRelativePath()) and
  cls.getName() = exampleReturnClass(exported.getParent())
select "clean_engineering:OoadClass:" + slash(cls.getFile().getRelativePath()) + ":" + cls.getName(),
  exampleId(file, name), "demonstratedThrough", 6, "relationship"
