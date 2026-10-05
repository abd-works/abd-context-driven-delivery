/**
 * @name step-scopes-examples
 * @kind problem
 * @id cdd/stories/edges/step-scopes-examples
 */

import javascript
import stories
import members

from
  CallExpr step, MethodCallExpr call, MethodDefinition callee, ExportNamedDeclaration decl,
  VarDecl exported, string file, string name, string exampleFilePath, string exampleName, string parent, string child
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
  exampleFilePath = slash(decl.getFile().getRelativePath()) and
  parent = stepId(file, stepLine(step), name) and
  child = exampleId(exampleFilePath, exampleName)
select parent, child, "scopes", 2, "grouped"
