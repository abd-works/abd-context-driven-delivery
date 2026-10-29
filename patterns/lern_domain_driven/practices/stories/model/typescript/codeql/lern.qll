import javascript
import stories

bindingset[path]
string fileSlash(string path) { result = path.replaceAll("\\", "/") }

string fileOf(AstNode node) { result = fileSlash(node.getFile().getRelativePath()) }

predicate sharedStoryCall(CallExpr call, string name, string file) {
  call.getCalleeName() = "shareStory" and
  name = call.getArgument(0).(StringLiteral).getValue() and
  file = fileOf(call) and
  file.regexpMatch("tests/[^/]+/[^/]+/[^/]+\\.story\\.shared\\.ts")
}

bindingset[file, name]
string storySharedId(string file, string name) { result = "stories:StoryShared:" + fileSlash(file) + ":" + name }

bindingset[kind, file, name]
string specId(string kind, string file, string name) { result = "stories:" + kind + ":" + fileSlash(file) + ":" + name }

predicate specFile(File file, string kind) {
  file.getBaseName().matches("%.story.domain.spec.ts") and kind = "DomainSpec"
  or
  file.getBaseName().matches("%.story.server.spec.ts") and kind = "ServerSpec"
  or
  file.getBaseName().matches("%.story.playwright.ts") and kind = "PlaywrightSpec"
}

string specNodeId(File file) {
  exists(string kind |
    specFile(file, kind) and
    result = specId(kind, fileSlash(file.getRelativePath()), file.getBaseName())
  )
}

string storyStem(File file) { result = file.getBaseName().regexpCapture("(.*)\\.story\\..*", 1) }

predicate sameStoryFile(File spec, File shared) {
  spec.getParentContainer() = shared.getParentContainer() and
  storyStem(spec) = storyStem(shared) and
  shared.getBaseName().matches("%.story.shared.ts")
}

predicate specExecutes(CallExpr specCall, CallExpr shared) {
  exists(File spec, File sharedFile, string title |
    specFile(spec, _) and
    specCall.getFile() = spec and
    specCall.getCalleeName() = ["withStory", "story"] and
    title = specCall.getArgument(0).(StringLiteral).getValue() and
    sameStoryFile(spec, sharedFile) and
    sharedStoryCall(shared, title, _) and
    shared.getFile() = sharedFile
  )
}

string aggregateOfImport(ImportDeclaration imp) {
  result = "ddd:Aggregate:src/" + imp.getImportedPathString().regexpCapture("(?:@src/|[.]*/)?src/([^/]+)/.*", 1)
  or
  result = "ddd:Aggregate:src/" + imp.getImportedPathString().regexpCapture("@src/([^/]+)/.*", 1)
}

