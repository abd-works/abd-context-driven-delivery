/**
 * @name Then step observes
 * @description A then step observes the property or operation it asserts.
 * @kind problem
 * @id cdd/practice-graph/step-observes
 */

import javascript
import story_query

predicate observed(CallExpr step, string className, string member, string kind, string label) {
  step.getCalleeName() = ["then", "and", "but"] and
  storyFile(step.getFile()) and
  label = step.getArgument(0).(StringLiteral).getValue() and
  (
    exists(PropAccess access |
      access.getEnclosingFunction() = step.getAnArgument() and
      member = access.getPropertyName() and
      className = receiverClass(access.getBase()) and
      kind = "property"
    )
    or
    exists(MethodCallExpr access |
      access.getEnclosingFunction() = step.getAnArgument() and
      member = access.getMethodName() and
      not member = ["toBe", "toEqual", "toBeNull", "toHaveLength", "toContain", "toBeTruthy"] and
      className = receiverClass(access.getReceiver()) and
      kind = "operation"
    )
  )
}

from CallExpr step, string className, string member, string kind, string label
where observed(step, className, member, kind, label)
select step, step.getFile().getRelativePath(), stepLine(step), className,
  member, kind, label
