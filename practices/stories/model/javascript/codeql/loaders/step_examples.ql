/**
 * @name Step examples
 * @description A given or then assigns a class variable the rest of the story uses,
 * or a then evaluates that variable. The example is the variable. Its source is the
 * operation called to create it, or the expression that created it.
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

Expr assignedValue(AssignExpr assign) {
  result = assign.getRhs().(AwaitExpr).getOperand()
  or
  not assign.getRhs() instanceof AwaitExpr and result = assign.getRhs()
}

predicate classVariable(VarDecl decl, string variable, string className) {
  storyFile(decl.getFile()) and
  variable = decl.getName() and
  className = typeName(decl.getTypeAnnotation())
}

predicate assigning(CallExpr step, VarDecl decl, Expr value) {
  exists(AssignExpr assign, VarAccess lhs |
    inStep(step, assign) and
    lhs = assign.getLhs() and
    decl = lhs.getVariable().getADeclaration() and
    value = assignedValue(assign)
  )
}

predicate usedLater(CallExpr step, VarDecl decl) {
  exists(CallExpr later, VarAccess use |
    later.getFile() = step.getFile() and
    later.getCalleeName() = ["given", "when", "then", "and", "but"] and
    storyTitle(later) = storyTitle(step) and
    use.getVariable().getADeclaration() = decl and
    inStep(later, use) and
    use.getLocation().getStartLine() > stepLine(step)
  )
}

predicate evaluates(CallExpr step, VarDecl decl) {
  step.getCalleeName() = ["then", "and", "but"] and
  storyFile(step.getFile()) and
  exists(Expr use, VarAccess base |
    inStep(step, use) and
    (
      base = use.(PropAccess).getBase()
      or
      base = use.(MethodCallExpr).getReceiver() and
      not use.(MethodCallExpr).getMethodName() =
        ["toBe", "toEqual", "toBeNull", "toHaveLength", "toContain", "toBeTruthy"]
    ) and
    decl = base.getVariable().getADeclaration()
  )
}

predicate creatorAt(Expr value, string file, int start, int end) {
  exists(Function fn |
    fn = value.(InvokeExpr).getResolvedCallee() and
    file = fn.getFile().getRelativePath() and
    start = fn.getLocation().getStartLine() and
    end = fn.getLocation().getEndLine()
  )
  or
  not exists(Function fn | fn = value.(InvokeExpr).getResolvedCallee()) and
  file = value.getFile().getRelativePath() and
  start = value.getLocation().getStartLine() and
  end = value.getLocation().getEndLine()
}

predicate activeValue(CallExpr step, VarDecl decl, Expr value) {
  assigning(step, decl, value)
  or
  exists(CallExpr earlier |
    evaluates(step, decl) and
    assigning(earlier, decl, value) and
    earlier.getFile() = step.getFile() and
    storyTitle(earlier) = storyTitle(step) and
    stepLine(earlier) < stepLine(step) and
    not exists(CallExpr between |
      assigning(between, decl, _) and
      between.getFile() = step.getFile() and
      storyTitle(between) = storyTitle(step) and
      stepLine(between) > stepLine(earlier) and
      stepLine(between) < stepLine(step)
    )
  )
}

from CallExpr step, VarDecl decl, string variable, string className, Expr value, string creatorFile,
  int creatorStart, int creatorEnd
where
  classVariable(decl, variable, className) and
  activeValue(step, decl, value) and
  (assigning(step, decl, value) and usedLater(step, decl) or evaluates(step, decl)) and
  creatorAt(value, creatorFile, creatorStart, creatorEnd)
select step, variable, step.getFile().getRelativePath(), stepLine(step), className, creatorFile,
  creatorStart, creatorEnd
