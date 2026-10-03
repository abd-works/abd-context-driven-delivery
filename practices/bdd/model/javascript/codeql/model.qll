import javascript
import subject_filter

predicate mambaIt(CallExpr call) { call.getCalleeName() = "it" }

predicate mambaDescribe(CallExpr call) {
  call.getCalleeName() = "describe" or call.getCalleeName() = "description"
}

predicate mambaContext(CallExpr call) {
  call.getCalleeName() = "context" or call.getCalleeName() = "describe"
}

predicate expectCall(CallExpr call) { call.getCalleeName() = "expect" }

predicate twoAssertions(Function f) {
  count(CallExpr call | call.getEnclosingFunction() = f and expectCall(call)) > 1
}

predicate internalDescribe(CallExpr call) {
  exists(string label |
    label = call.getArgument(0).(StringLiteral).getValue() and
    mambaDescribe(call) and
    (
      label.matches("%Manager%") or
      label.matches("%Service%") or
      label.matches("%Runner%") or
      label.matches("%Hub%") or
      label.matches("%SessionLog%")
    )
  )
}

predicate whenContext(CallExpr call) {
  mambaContext(call) and
  call.getArgument(0).(StringLiteral).getValue().toLowerCase().matches("when %")
}

predicate observesPrivate(CallExpr call) {
  expectCall(call) and
  exists(PropAccess access |
    access = call.getArgument(0) and
    access.getPropertyName().regexpMatch("^_[^_].*")
  )
}

predicate relativeInternalMock(CallExpr call, string target) {
  exists(string name |
    name = call.getCalleeName() and
    (name = "mock" or name = "spyOn") and
    target = call.getArgument(0).(StringLiteral).getValue() and
    (
      target.matches("./%") or
      target.matches("../%") or
      target.matches(".%")
    )
  )
}
