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
    not cls.getName().matches("%(Client|Node|Repository|Exception|Error)") and
    result = "ddd:EntityRoot:" + fileOf(cls) + ":" + cls.getName()
  )
  or
  exists(Function func |
    func = node and
    func.getName().matches("%View") and
    result = "ddd:DomainView:" + fileOf(func) + ":" + func.getName()
  )
  or
  not exists(ClassDefinition cls | cls = node) and
  not exists(Function func | func = node and func.getName().matches("%View")) and
  result = "ddd:Entity:" + fileOf(node) + ":" + node.getLocation().getStartLine().toString()
}
