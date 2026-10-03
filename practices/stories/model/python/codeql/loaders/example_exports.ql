/**
 * @name Example factory exports
 * @description export const in *.examples.ts — the example name and the domain class it constructs.
 * @kind problem
 * @id cdd/practice-graph/example-exports
 */

import python

from ExportNamedDeclaration decl, VarDecl exported, VariableDeclarator declarator, File file, string className
where
  file = decl.getFile() and
  file.getBaseName().matches("%.examples.py") and
  exported = decl.getADecl() and
  declarator.getBindingPattern().getABindingVarRef() = exported and
  (
    exists(NewExpr neu |
      neu.getParent*() = declarator.getInit() and
      className = neu.getCalleeName()
    )
    or
    not exists(NewExpr neu |
      exists(declarator.getInit()) and
      neu.getParent*() = declarator.getInit() and
      exists(neu.getCalleeName())
    ) and
    className = ""
  )
select exported, exported.getName(), file.getRelativePath(),
  exported.getLocation().getStartLine(), className, exported.getLocation().getEndLine()
