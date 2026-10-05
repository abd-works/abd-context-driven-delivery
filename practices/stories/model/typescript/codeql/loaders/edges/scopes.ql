/**
 * @name scopes
 * @kind problem
 * @id cdd/stories/edges/scopes
 */

import javascript
import stories
import members

from
  CallExpr step, MethodCallExpr call, MethodDefinition callee, ExportNamedDeclaration decl,
  VarDecl exported, string file, string name, string exampleFilePath, string exampleName
where
  step.getCalleeName() = "when" and
  storyFile(step.getFile()) and
  call.getEnclosingFunction() = step.getAnArgument() and
  classOperation(callee) and
  callee.getName() = call.getMethodName() and
  exampleFile(decl.getFile()) and
  exported = decl.getADecl() and
  exampleName = exported.getName() and
  not exampleName.matches("seed%") and
  exampleReturnClass(exported.getParent()) = callee.getDeclaringType().getName() and
  file = slash(step.getFile().getRelativePath()) and
  name = "when " + step.getArgument(0).(StringLiteral).getValue() and
  exampleFilePath = slash(decl.getFile().getRelativePath())
select stepId(file, stepLine(step), name), exampleId(exampleFilePath, exampleName), "scopes", 2,
  "grouped"
