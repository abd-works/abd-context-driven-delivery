/**
 * @name step-scopes-examples
 * @kind problem
 * @id cdd/stories/edges/step-scopes-examples
 */

import javascript
import stories

from CallExpr step, CallExpr use, string exampleFile, string exampleName, string parent, string child
where
  storyStep(step, ["given", "when", "and", "but"], _, _, parent) and
  callInsideStep(step, use) and
  exampleName = use.getCalleeName() and
  exists(ExportNamedDeclaration decl |
    exampleExport(decl, exampleName, _, _) and
    exampleFile = slash(decl.getFile().getRelativePath())
  ) and
  child = exampleId(exampleFile, exampleName)
select parent, child, "scopes", 2, "grouped"
