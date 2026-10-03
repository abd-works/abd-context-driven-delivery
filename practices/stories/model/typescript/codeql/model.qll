import javascript
import subject_filter

predicate storyCall(CallExpr call) { call.getCalleeName() = "story" }

predicate scenarioCall(CallExpr call) { call.getCalleeName() = "scenario" }

predicate stepCall(CallExpr call, string keyword) {
  keyword = call.getCalleeName() and
  (keyword = "given" or keyword = "when" or keyword = "then" or keyword = "and" or keyword = "but")
}

predicate storyLabel(CallExpr call, string label) {
  storyCall(call) and label = call.getArgument(0).(StringLiteral).getValue()
}

predicate kebabPath(File file) {
  file.getRelativePath().regexpMatch(".*[A-Z_].*") and
  file.getBaseName().matches("%_story.test.ts")
}

bindingset[label]
predicate identifierStep(string label) {
  label.regexpMatch("[A-Za-z_][A-Za-z0-9_]*")
}
