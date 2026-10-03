import python
import subject_filter

predicate storyCall(Call call) { call.getFunc().(Name).getId() = "story" }

predicate scenarioCall(Call call) { call.getFunc().(Name).getId() = "scenario" }

predicate stepCall(Call call, string keyword) {
  keyword = call.getFunc().(Name).getId() and
  (keyword = "given" or keyword = "when" or keyword = "then" or keyword = "and" or keyword = "but")
}

predicate storyLabel(Call call, string label) {
  storyCall(call) and label = call.getArg(0).(StringLiteral).getValue()
}

predicate kebabPath(File file) {
  file.getRelativePath().regexpMatch(".*[A-Z_].*") and
  file.getBaseName().matches("%_story.test.py")
}

bindingset[label]
predicate identifierStep(string label) {
  label.regexpMatch("[A-Za-z_][A-Za-z0-9_]*")
}
