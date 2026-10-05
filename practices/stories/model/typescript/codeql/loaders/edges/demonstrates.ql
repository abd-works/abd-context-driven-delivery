/**
 * @name demonstrates
 * @kind problem
 * @id cdd/stories/edges/demonstrates
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
select exampleId(file, name),
  "clean_engineering:OoadClass:" + slash(cls.getFile().getRelativePath()) + ":" + cls.getName(),
  "demonstrates", 3, "grouped"
