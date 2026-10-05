/**
 * @name class-demonstrated-through-examples
 * @kind problem
 * @id cdd/stories/edges/class-demonstrated-through-examples
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
  parent = "clean_engineering:OoadClass:" + slash(cls.getFile().getRelativePath()) + ":" + cls.getName() and
  child = exampleId(file, name)
select parent, child, "demonstratedThrough", 6, "relationship"
