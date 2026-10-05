import javascript
import members

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

/** Line of the step keyword. Chained `.and()` / `.but()` use the keyword line, not the receiver. */
int stepLine(CallExpr call) {
  result = call.getCallee().(PropAccess).getLocation().getEndLine()
  or
  not call.getCallee() instanceof PropAccess and
  result = call.getCallee().getLocation().getStartLine()
}

int stepEnd(CallExpr call) {
  result = max(int line |
    line = call.getArgument(_).(Function).getLocation().getEndLine()
    or
    not exists(call.getArgument(_).(Function)) and line = call.getLocation().getEndLine()
  )
}

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

string subEpicFolder(File file) {
  result = slash(file.getRelativePath()).regexpCapture("(tests/[^/]+/[^/]+)/.*", 1)
}

bindingset[slug]
string titleCaseKebab(string slug) {
  slug.regexpMatch("^[^-]+$") and result = capitalize(slug)
  or
  exists(string first, string second |
    slug.regexpMatch("^[^-]+-[^-]+$") and
    first = slug.regexpCapture("^([^-]+)-([^-]+)$", 1) and
    second = slug.regexpCapture("^([^-]+)-([^-]+)$", 2) and
    result = capitalize(first) + " " + capitalize(second)
  )
  or
  exists(string first, string second, string third |
    slug.regexpMatch("^[^-]+-[^-]+-[^-]+$") and
    first = slug.regexpCapture("^([^-]+)-([^-]+)-([^-]+)$", 1) and
    second = slug.regexpCapture("^([^-]+)-([^-]+)-([^-]+)$", 2) and
    third = slug.regexpCapture("^([^-]+)-([^-]+)-([^-]+)$", 3) and
    result = capitalize(first) + " " + capitalize(second) + " " + capitalize(third)
  )
}

bindingset[folder]
string subEpicName(string folder) {
  result = titleCaseKebab(folder.regexpCapture(".*/([^/]+)$", 1))
}

bindingset[folder]
string subEpicId(string folder) {
  result = "stories:SubEpic:" + folder + ":" + subEpicName(folder)
}

string storyOwner(File file) {
  exists(string folder | folder = subEpicFolder(file) and result = subEpicId(folder))
  or
  not exists(subEpicFolder(file)) and result = epicId(epicFolder(file))
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

string typeName(TypeAnnotation type) {
  result = type.(TypeExpr).getAChild*().(LocalTypeAccess).getName()
}

string annotatedName(BindingPattern node) { result = typeName(node.getTypeAnnotation()) }

predicate exampleExport(ExportNamedDeclaration decl, string name, int start, int end) {
  exampleFile(decl.getFile()) and
  exists(VarDecl exported |
    exported = decl.getADecl() and
    name = exported.getName() and
    not name.matches("seed%") and
    (
      exists(FunctionDeclStmt fn |
        fn.getIdentifier() = exported and
        start = fn.getLocation().getStartLine() and
        end = fn.getLocation().getEndLine()
      )
      or
      exists(VariableDeclarator declarator |
        not exists(FunctionDeclStmt fn | fn.getIdentifier() = exported) and
        declarator.getBindingPattern() = exported and
        start = declarator.getLocation().getStartLine() and
        end = declarator.getLocation().getEndLine()
      )
    )
  )
}

Function exampleFactory(string file, string name) {
  exists(ExportNamedDeclaration decl, VarDecl exported |
    exampleExport(decl, name, _, _) and
    exported = decl.getADecl() and
    name = exported.getName() and
    file = slash(decl.getFile().getRelativePath()) and
    (
      result.(FunctionDeclStmt).getIdentifier() = exported
      or
      result = exported.getParent().(VariableDeclarator).getInit()
    )
  )
}

string exampleReturnClassName(string file, string name) {
  result = typeName(exampleFactory(file, name).getReturnTypeAnnotation())
}

predicate callInsideStep(CallExpr step, Expr inner) {
  inner.getEnclosingFunction*() = step.getAnArgument()
}

MethodDefinition resolvedMethod(MethodCallExpr call) {
  classOperation(result) and
  result.getName() = call.getMethodName() and
  (
    exists(VarAccess receiver, BindingPattern decl |
      receiver = call.getReceiver() and
      decl = receiver.getVariable().getADeclaration() and
      result.getDeclaringType().getName() = annotatedName(decl)
    )
    or
    exists(MethodDefinition owner |
      call.getReceiver() instanceof ThisExpr and
      call.getEnclosingFunction*() = owner.getBody() and
      result.getDeclaringType() = owner.getDeclaringType()
    )
    or
    not exists(VarAccess receiver, BindingPattern decl |
      receiver = call.getReceiver() and
      decl = receiver.getVariable().getADeclaration() and
      exists(annotatedName(decl))
    ) and
    not call.getReceiver() instanceof ThisExpr and
    count(MethodDefinition other |
      classOperation(other) and other.getName() = call.getMethodName()
    ) = 1
    or
    exists(string file, string exampleName |
      call.getReceiver().(CallExpr).getCalleeName() = exampleName and
      result.getDeclaringType().getName() = exampleReturnClassName(file, exampleName)
    )
  )
}

string operationNodeId(MethodDefinition method) {
  result =
    "clean_engineering:Operation:" + slash(method.getFile().getRelativePath()) + ":" +
      method.getName() + ":" + method.getDeclaringType().getName()
}

string classNodeId(ClassDefinition cls) {
  result = "clean_engineering:OoadClass:" + slash(cls.getFile().getRelativePath()) + ":" + cls.getName()
}

string propertyNodeId(FieldDefinition field) {
  result =
    "clean_engineering:Property:" + slash(field.getFile().getRelativePath()) + ":" + field.getName() +
      ":" + field.getDeclaringType().getName()
}

predicate storyStep(CallExpr step, string keyword, string text, string file, string id) {
  stepCall(step, keyword) and
  storyFile(step.getFile()) and
  text = step.getArgument(0).(StringLiteral).getValue() and
  file = slash(step.getFile().getRelativePath()) and
  id = stepId(file, stepLine(step), keyword + " " + text)
}

predicate continuesStep(CallExpr step, CallExpr prior) {
  stepCall(step, ["and", "but"]) and
  stepCall(prior, ["given", "when", "then"]) and
  prior.getFile() = step.getFile() and
  prior.getEnclosingFunction() = step.getEnclosingFunction() and
  stepLine(prior) < stepLine(step) and
  not exists(CallExpr between |
    stepCall(between, ["given", "when", "then"]) and
    between.getFile() = step.getFile() and
    between.getEnclosingFunction() = step.getEnclosingFunction() and
    stepLine(between) > stepLine(prior) and
    stepLine(between) < stepLine(step)
  )
}

predicate continuesThen(CallExpr step) {
  stepCall(step, ["and", "but"]) and
  exists(CallExpr prior |
    stepCall(prior, "then") and
    prior.getFile() = step.getFile() and
    prior.getEnclosingFunction() = step.getEnclosingFunction() and
    stepLine(prior) < stepLine(step) and
    not exists(CallExpr between |
      stepCall(between, ["given", "when", "then"]) and
      between.getFile() = step.getFile() and
      between.getEnclosingFunction() = step.getEnclosingFunction() and
      stepLine(between) > stepLine(prior) and
      stepLine(between) < stepLine(step)
    )
  )
}

