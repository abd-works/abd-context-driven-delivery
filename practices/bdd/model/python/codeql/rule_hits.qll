import python
import subject_filter
import model

predicate graphRuleHit(AstNode subject, string message, AstNode contributor, string slug) {
  slug = "observable-behavior" and
  exists(Call call |
    inSubject(call) and
    observesPrivate(call) and
    subject = call and
    contributor = call and
    message = "Assertion observes a private attribute instead of stakeholder-visible behaviour."
  )
  or
  slug = "describe-is-subject-not-internal" and
  exists(Call call, string label |
    inSubject(call) and
    internalDescribe(call) and
    label = call.getArg(0).(StringLiteral).getText() and
    subject = call and
    contributor = call and
    message = "Describe names internal type '" + label + "' instead of a domain subject."
  )
  or
  slug = "state-not-when" and
  exists(Call call |
    inSubject(call) and
    whenContext(call) and
    subject = call and
    contributor = call and
    message = "Nested state is named with 'when' instead of a condition."
  )
  or
  slug = "one-assertion-per-test" and
  exists(With block, Call itCall |
    inSubject(block) and
    itCall = block.getContextExpr() and
    mambaIt(itCall) and
    count(Call assertion | expectCall(assertion) and assertion.getParentNode*() = block) > 1 and
    subject = itCall and
    contributor = itCall and
    message = "Example has more than one assertion."
  )
  or
  slug = "layer-isolation" and
  exists(Call call, string target |
    inSubject(call) and
    relativeInternalMock(call, target) and
    subject = call and
    contributor = call and
    message =
      "Mock targets internal module '" + target +
        "'. Only mock external boundaries (APIs, databases, third-party services)."
  )
}
