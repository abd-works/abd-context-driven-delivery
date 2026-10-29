import javascript

bindingset[path]
string fileSlash(string path) { result = path.replaceAll("\\", "/") }

string fileOf(AstNode node) { result = fileSlash(node.getFile().getRelativePath()) }

string factId(AstNode node) {
  exists(CallExpr call, string name |
    call = node and
    call.getCalleeName() = "shareStory" and
    name = call.getArgument(0).(StringLiteral).getValue() and
    result = "stories:StoryShared:" + fileOf(call) + ":" + name
  )
  or
  exists(string file, string base |
    file = fileOf(node) and
    base = node.getFile().getBaseName() and
    (
      base.matches("%.story.domain.spec.ts") and result = "stories:DomainSpec:" + file + ":" + base
      or
      base.matches("%.story.server.spec.ts") and result = "stories:ServerSpec:" + file + ":" + base
      or
      base.matches("%.story.playwright.ts") and result = "stories:PlaywrightSpec:" + file + ":" + base
    )
  )
  or
  not exists(CallExpr call | call = node and call.getCalleeName() = "shareStory") and
  not node.getFile().getBaseName().matches("%.story.domain.spec.ts") and
  not node.getFile().getBaseName().matches("%.story.server.spec.ts") and
  not node.getFile().getBaseName().matches("%.story.playwright.ts") and
  result = "stories:Story:" + fileOf(node) + ":" + node.getLocation().getStartLine().toString()
}
