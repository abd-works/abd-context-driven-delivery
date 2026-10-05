/**
 * @name example-demonstrates-class
 * @kind problem
 * @id cdd/stories/edges/example-demonstrates-class
 */

import javascript
import stories

from ExportNamedDeclaration decl, VarDecl exported, ClassDefinition cls, string file, string name, string parent, string child
where
  exampleFile(decl.getFile()) and
  exported = decl.getADecl() and
  name = exported.getName() and
  not name.matches("seed%") and
  file = slash(decl.getFile().getRelativePath()) and
  cls.getName() = exampleReturnClass(exported.getParent()) and
  parent = exampleId(file, name) and
  child = "clean_engineering:OoadClass:" + slash(cls.getFile().getRelativePath()) + ":" + cls.getName()
select parent, child, "demonstrates", 3, "grouped"
