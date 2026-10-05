import javascript

predicate storyCall(CallExpr call) { call.getCalleeName() = ["story", "shareStory"] }

predicate scenarioCall(CallExpr call) { call.getCalleeName() = "scenario" }

predicate stepCall(CallExpr call) {
  call.getCalleeName() = ["given", "when", "then", "and", "but"]
}

predicate stepCall(CallExpr call, string keyword) {
  keyword = call.getCalleeName() and
  stepCall(call)
}

predicate storyFile(File file) {
  file.getRelativePath().regexpMatch(".*story.*")
}

int stepLine(CallExpr call) { result = call.getLocation().getStartLine() }

string storyTitle(CallExpr inner) {
  exists(CallExpr story |
    storyCall(story) and
    inner.getEnclosingFunction*() = story.getArgument(1).(Function) and
    result = story.getArgument(0).(StringLiteral).getValue()
  )
}

string scenarioTitle(CallExpr inner) {
  exists(CallExpr scenario |
    scenarioCall(scenario) and
    inner.getEnclosingFunction*() = scenario.getArgument(1).(Function) and
    result = scenario.getArgument(0).(StringLiteral).getValue()
  )
}

string backgroundTitle(CallExpr inner) {
  exists(CallExpr background |
    background.getCalleeName() = "background" and
    inner.getEnclosingFunction*() = background.getArgument(1).(Function) and
    result = background.getArgument(0).(StringLiteral).getValue()
  )
  or
  not exists(CallExpr background |
    background.getCalleeName() = "background" and
    inner.getEnclosingFunction*() = background.getArgument(1).(Function)
  ) and
  result = ""
}

string receiverClass(Expr receiver) {
  exists(string name |
    name = receiver.(VarAccess).getName() and
    name.regexpMatch(".*[Cc]ustomer.*") and
    not name.regexpMatch(".*[Aa]ccount.*") and
    result = "Customer"
  )
  or
  exists(string name |
    name = receiver.(VarAccess).getName() and
    (
      name.regexpMatch(".*[Aa]ccount.*") or
      name.regexpMatch(".*[Rr]epository.*")
    ) and
    result = "AccountCredentials"
  )
}
