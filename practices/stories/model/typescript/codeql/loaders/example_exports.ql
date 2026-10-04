/**
 * @name Example factory exports
 * @description Exported example factories in *.examples.ts.
 * @kind problem
 * @id cdd/practice-graph/example-exports
 */

import javascript

predicate exampleFile(File file) {
  file.getBaseName().regexpMatch(".*\\.examples\\.[jt]sx?")
}

string exampleClass(VarDecl exported) {
  result = exported.getParent().(Function).getReturnTypeAnnotation().(LocalTypeAccess).getName()
  or
  exists(VariableDeclarator declarator, NewExpr neu |
    declarator.getBindingPattern().getABindingVarRef() = exported and
    neu.getParent*() = declarator.getInit() and
    result = neu.getCalleeName()
  )
}

from ExportNamedDeclaration decl, VarDecl exported, File file, string className
where
  file = decl.getFile() and
  exampleFile(file) and
  exported = decl.getADecl() and
  (
    className = exampleClass(exported)
    or
    not exists(exampleClass(exported)) and className = ""
  )
select exported, exported.getName(), file.getRelativePath(), exported.getLocation().getStartLine(),
  className, exported.getLocation().getEndLine()
