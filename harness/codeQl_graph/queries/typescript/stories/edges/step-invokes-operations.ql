/**
 * @name step-invokes-operations
 * @kind problem
 * @id cdd/stories/edges/step-invokes-operations
 */

import javascript
import stories.stories
import members

from CallExpr step, MethodCallExpr call, MethodDefinition callee, string text, string file, string name, string parent, string child
where
  step.getCalleeName() = ["given", "when", "and", "but"] and
  storyFile(step.getFile()) and
  call.getEnclosingFunction() = step.getAnArgument() and
  classOperation(callee) and
  callee.getName() = call.getMethodName() and
  callee.getDeclaringType().getName() = receiverClass(call.getReceiver()) and
  text = step.getArgument(0).(StringLiteral).getValue() and
  file = slash(step.getFile().getRelativePath()) and
  name = step.getCalleeName() + " " + text and
  parent = stepId(file, stepLine(step), name) and
  child = "clean_engineering:Operation:" + slash(callee.getFile().getRelativePath()) + ":" + callee.getName()
    + ":" + callee.getDeclaringType().getName()
select parent, child, "invokes", 5, "relationship"
