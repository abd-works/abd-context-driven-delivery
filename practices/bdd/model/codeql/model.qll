import python
import subject_filter

predicate mambaIt(Call call) { call.getFunc().(Name).getId() = "it" }

predicate mambaDescribe(Call call) { call.getFunc().(Name).getId() = "description" }

predicate mambaContext(Call call) { call.getFunc().(Name).getId() = "context" }

predicate expectCall(Call call) { call.getFunc().(Name).getId() = "expect" }

predicate twoAssertions(Function f) { count(Call call | call.getScope() = f and expectCall(call)) > 1 }

predicate internalDescribe(Call call) {
  exists(string label |
    label = call.getArg(0).(StringLiteral).getText() and
    (
      mambaDescribe(call) or
      exists(With block | block.getContextExpr() = call)
    ) and
    (
      label.matches("%Manager%") or
      label.matches("%Service%") or
      label.matches("%Runner%") or
      label.matches("%Hub%") or
      label.matches("%SessionLog%")
    )
  )
}

predicate whenContext(Call call) {
  mambaContext(call) and
  call.getArg(0).(StringLiteral).getText().toLowerCase().matches("when %")
}

predicate observesPrivate(Call call) {
  expectCall(call) and
  exists(Attribute attr |
    attr = call.getArg(0) and
    attr.getName().matches("\\_%") and
    not attr.getName().matches("\\_\\_%")
  )
}
