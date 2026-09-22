/**
 * @name Story steps
 * @description given/when/then/.and/.but calls — keyword and label from the TypeScript test.
 * @kind problem
 * @id cdd/practice-graph/steps
 */

import javascript

predicate isStepName(string name) {
  name = "given" or
  name = "when" or
  name = "then" or
  name = "and" or
  name = "but"
}

from CallExpr call, string callee, Expr arg, File file
where
  callee = call.getCalleeName() and
  isStepName(callee) and
  arg = call.getArgument(0) and
  file = call.getFile() and
  file.getBaseName().matches("%_story.test.ts")
select call, callee, arg, file.getRelativePath(), call.getLocation().getStartLine()
