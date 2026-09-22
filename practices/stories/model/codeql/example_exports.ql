/**
 * @name Example factory exports
 * @description export const in *.examples.ts — the example name and the domain class it constructs.
 * @kind problem
 * @id cdd/practice-graph/example-exports
 */

import javascript

from ExportVarDecl decl, File file
where
  file = decl.getFile() and
  file.getBaseName().matches("%.examples.ts")
select decl, decl.getName(), file.getRelativePath(), decl.getLocation().getStartLine()
