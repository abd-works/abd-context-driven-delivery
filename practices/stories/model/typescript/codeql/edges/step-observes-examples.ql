/**
 * @name step-observes-examples
 * @kind problem
 * @id cdd/stories/edges/step-observes-examples
 */

import javascript
import stories

from CallExpr step, Expr use, string exampleFile, string exampleName, string parent, string child
where
  (
    storyStep(step, "then", _, _, parent)
    or
    continuesThen(step) and storyStep(step, _, _, _, parent)
  ) and
  callInsideStep(step, use) and
  exists(ExportNamedDeclaration decl |
    exampleExport(decl, exampleName, _, _) and
    exampleFile = slash(decl.getFile().getRelativePath())
  ) and
  (
    exampleName = use.(CallExpr).getCalleeName()
    or
    exampleName = use.(VarAccess).getName()
    or
    exampleName = use.(PropAccess).getBase().(VarAccess).getName()
  ) and
  child = exampleId(exampleFile, exampleName)
select parent, child, "observes", 8, "relationship"
