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
  file.getBaseName().matches("%_story.test.js")
}

bindingset[label]
predicate identifierStep(string label) {
  label.regexpMatch("[A-Za-z_][A-Za-z0-9_]*")
}

predicate nestedInStory(CallExpr inner, CallExpr story) {
  storyCall(story) and
  inner.getEnclosingFunction*() = story.getArgument(1).(Function)
}

int scenarioCount(CallExpr story) {
  result = count(CallExpr scenario | scenarioCall(scenario) and nestedInStory(scenario, story))
}

predicate tooFewOrManyScenarios(CallExpr story) {
  exists(int n | n = scenarioCount(story) and (n < 4 or n > 9))
}

predicate siblingStories(string left, string right, File file) {
  exists(CallExpr a, CallExpr b |
    storyCall(a) and
    storyCall(b) and
    a.getFile() = file and
    b.getFile() = file and
    left = a.getArgument(0).(StringLiteral).getValue() and
    right = b.getArgument(0).(StringLiteral).getValue() and
    left < right
  )
}

bindingset[left, right]
predicate similarSiblingNames(string left, string right) {
  left.length() - right.length() <= 2 and
  right.length() - left.length() <= 2
}

predicate untracedStory(CallExpr call, string name) {
  storyLabel(call, name) and
  not exists(ClassDefinition cls |
    name.toLowerCase().matches("%" + cls.getName().toLowerCase() + "%")
  )
}
