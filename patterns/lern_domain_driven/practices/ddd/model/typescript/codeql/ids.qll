import javascript

bindingset[path]
string fileSlash(string path) { result = path.replaceAll("\\", "/") }

string fileOf(AstNode node) { result = fileSlash(node.getFile().getRelativePath()) }

string factId(AstNode node) {
  exists(ClassDefinition cls |
    cls = node and
    cls.getFile().getBaseName().matches("%-client.tsx") and
    cls.getName().matches("%Client") and
    result = "ddd:DomainClient:" + fileOf(cls) + ":" + cls.getName()
  )
  or
  exists(ClassDefinition cls |
    cls = node and
    cls.getFile().getBaseName().matches("%-node.ts") and
    cls.getName().matches("%Node") and
    result = "ddd:DomainNode:" + fileOf(cls) + ":" + cls.getName()
  )
  or
  exists(ClassDefinition cls |
    cls = node and
    cls.getName().matches("%Repository") and
    result = "ddd:Repository:" + fileOf(cls) + ":" + cls.getName()
  )
  or
  exists(ClassDefinition cls |
    cls = node and
    not cls.getName().matches("%(Client|Node|Repository|Exception|Error|View)") and
    result = "ddd:EntityRoot:" + fileOf(cls) + ":" + cls.getName()
  )
  or
  exists(Function func |
    func = node and
    func.getName().matches("%View") and
    result = "ddd:DomainView:" + fileOf(func) + ":" + func.getName()
  )
  or
  exists(MethodCallExpr call, string http, string path |
    call = node and
    http = call.getCalleeName() and
    http = ["get", "post"] and
    path = call.getArgument(0).(StringLiteral).getValue() and
    result = "ddd:Destination:" + fileOf(call) + ":" + http.toUpperCase() + " " + path
  )
  or
  not exists(ClassDefinition cls | cls = node) and
  not exists(Function func | func = node and func.getName().matches("%View")) and
  not exists(MethodCallExpr call | call = node and call.getCalleeName() = ["get", "post"]) and
  result = "ddd:Entity:" + fileOf(node) + ":" + node.getLocation().getStartLine().toString()
}
