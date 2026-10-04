/**
 * @name Step examples
 * @description A given or then assigns a class to a variable the rest of the scenario uses,
 * or a then evaluates that class.
 * @kind problem
 * @id cdd/practice-graph/step-examples
 */

import javascript
import story_query

predicate inStep(CallExpr step, Expr use) {
  use.getFile() = step.getFile() and
  (
    use.getEnclosingFunction() = step.getAnArgument()
    or
    exists(MethodCallExpr chain |
      chain.getCalleeName() = ["and", "but"] and
      chain.getReceiver() = step and
      use.getEnclosingFunction() = chain.getAnArgument()
    )
  )
}

predicate assignedClass(CallExpr step, string className) {
  step.getCalleeName() = ["given", "then", "and", "but", "background"] and
  storyFile(step.getFile()) and
  exists(AssignExpr assign, VarAccess lhs, VarDecl variable, CallExpr later, VarAccess use |
    inStep(step, assign) and
    lhs = assign.getLhs() and
    variable = lhs.getVariable().getADeclaration().(VarDecl) and
    className = typeName(variable.getTypeAnnotation()) and
    later.getFile() = step.getFile() and
    later.getCalleeName() = ["given", "when", "then", "and", "but"] and
    storyTitle(later) = storyTitle(step) and
    use.getVariable().getADeclaration().(VarDecl) = variable and
    inStep(later, use) and
    use.getLocation().getStartLine() > stepLine(step)
  )
}

predicate evaluatedClass(CallExpr step, string className) {
  step.getCalleeName() = ["then", "and", "but"] and
  storyFile(step.getFile()) and
  exists(Expr use |
    inStep(step, use) and
    (
      className = receiverClass(use.(PropAccess).getBase())
      or
      className = receiverClass(use.(MethodCallExpr).getReceiver()) and
      not use.(MethodCallExpr).getMethodName() =
        ["toBe", "toEqual", "toBeNull", "toHaveLength", "toContain", "toBeTruthy"]
    )
  )
}

from CallExpr step, string className
where assignedClass(step, className) or evaluatedClass(step, className)
select step, className, step.getFile().getRelativePath(), stepLine(step)
