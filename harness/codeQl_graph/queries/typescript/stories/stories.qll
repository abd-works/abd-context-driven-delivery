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

string backgroundTitle(CallExpr call) {
  call.getCalleeName() = "background" and
  exists(CallExpr given |
    given.getCalleeName() = "given" and
    given.getEnclosingFunction() = call.getArgument(0).(Function) and
    result = given.getArgument(0).(StringLiteral).getValue()
  )
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

bindingset[path]
string slash(string path) { result = path.replaceAll("\\", "/") }

string storiesPracticeId() { result = "stories:Practice:.:stories" }

string epicFolder(File file) {
  result = slash(file.getRelativePath()).regexpCapture("(tests/[^/]+)/.*", 1)
}

bindingset[folder]
string epicName(string folder) {
  folder.matches("%onboard-a-customer%") and result = "Onboard A Customer"
  or
  not folder.matches("%onboard-a-customer%") and result = folder.regexpCapture(".*/([^/]+)$", 1)
}

bindingset[folder]
string epicId(string folder) {
  result = "stories:Epic:" + folder + ":" + epicName(folder)
}

bindingset[file, name]
string storyId(string file, string name) { result = "stories:Story:" + slash(file) + ":" + name }

bindingset[file, name]
string scenarioId(string file, string name) {
  result = "stories:Scenario:" + slash(file) + ":" + name
}

bindingset[file, label]
string backgroundId(string file, string label) {
  result = "stories:Background:" + slash(file) + ":" + label
}

bindingset[file, line, name]
string stepId(string file, int line, string name) {
  result = "stories:Step:" + slash(file) + ":" + name + ":" + line.toString()
}

bindingset[file, name]
string exampleId(string file, string name) { result = "stories:Example:" + slash(file) + ":" + name }

predicate exampleFile(File file) { file.getBaseName().regexpMatch(".*\\.examples\\.[jt]sx?") }

string exampleReturnClass(Function f) {
  result = f.getReturnTypeAnnotation().(LocalTypeAccess).getName()
}

