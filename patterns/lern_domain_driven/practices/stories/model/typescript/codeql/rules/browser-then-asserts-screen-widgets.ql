/**
 * @name browser-then-asserts-screen-widgets
 * @practice stories
 * @pattern lern_domain_driven
 * @fidelity acceptance_tests
 * @node function
 * @id stories/acceptance_tests/browser-then-asserts-screen-widgets
 */

import javascript
import subject_filter
import model

predicate playwrightStory(File file) {
  file.getBaseName().regexpMatch(".*\\.story\\.playwright\\.ts") or
  file.getBaseName().regexpMatch(".*_e2e\\.spec\\.ts")
}

from CallExpr thenStep, StringLiteral pathLiteral, string message, AstNode contributor
where
  playwrightStory(thenStep.getFile()) and
  inSubject(thenStep) and
  thenStep.getCalleeName() = "then" and
  exists(MethodCallExpr toHaveText, MethodCallExpr getByTestId, CallExpr expectCall |
    toHaveText.getMethodName() = "toHaveText" and
    pathLiteral = toHaveText.getArgument(0) and
    pathLiteral.getValue().matches("/%") and
    expectCall = toHaveText.getReceiver() and
    expectCall.getCalleeName() = "expect" and
    getByTestId = expectCall.getArgument(0) and
    getByTestId.getMethodName() = "getByTestId" and
    getByTestId.getArgument(0).(StringLiteral).getValue().matches("%destination%") and
    thenStep.getAnArgument() = toHaveText.getEnclosingFunction()
  ) and
  message =
    "A browser Then on a form screen asserts the headings, fields, links, and buttons on that screen." and
  contributor = pathLiteral
select thenStep, message, contributor
