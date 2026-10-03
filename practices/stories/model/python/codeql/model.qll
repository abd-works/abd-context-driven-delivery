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

predicate storyWith(With block, string name) {
  exists(Call call |
    block.getContextExpr() = call and
    storyCall(call) and
    name = call.getArg(0).(StringLiteral).getValue()
  )
}

predicate nestedIn(With inner, With outer) { inner.getParentNode+() = outer }

int scenarioCount(With story) {
  result =
    count(With block, Call call |
      nestedIn(block, story) and
      block.getContextExpr() = call and
      scenarioCall(call)
    )
}

predicate tooFewOrManyScenarios(With story) {
  exists(int n | n = scenarioCount(story) and (n < 4 or n > 9))
}

predicate siblingStories(string left, string right, File file) {
  exists(Call a, Call b |
    storyCall(a) and
    storyCall(b) and
    a.getFile() = file and
    b.getFile() = file and
    left = a.getArg(0).(StringLiteral).getValue() and
    right = b.getArg(0).(StringLiteral).getValue() and
    left < right
  )
}

bindingset[left, right]
predicate similarSiblingNames(string left, string right) {
  left.length() - right.length() <= 2 and
  right.length() - left.length() <= 2
}

predicate untracedStory(Call call, string name) {
  storyLabel(call, name) and
  not exists(Class cls | name.toLowerCase().matches("%" + cls.getName().toLowerCase() + "%"))
}
