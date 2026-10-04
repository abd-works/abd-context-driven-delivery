/**
 * @name When step invokes
 * @description A when step invokes the operation its typed receiver calls.
 * @kind problem
 * @id cdd/practice-graph/step-invokes
 */

import javascript
import story_query

from CallExpr step, MethodCallExpr call, string className, string method, string label
where
  step.getCalleeName() = ["given", "when", "and", "but"] and
  storyFile(step.getFile()) and
  call.getEnclosingFunction() = step.getAnArgument() and
  method = call.getMethodName() and
  not method = ["then", "catch", "toBe", "toEqual", "toBeNull", "toHaveLength"] and
  className = receiverClass(call.getReceiver()) and
  label = step.getArgument(0).(StringLiteral).getValue()
select step, step.getFile().getRelativePath(), stepLine(step), className,
  method, label
