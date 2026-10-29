import javascript
import ddd

bindingset[path]
string fileSlash(string path) { result = path.replaceAll("\\", "/") }

string fileOf(AstNode node) { result = fileSlash(node.getFile().getRelativePath()) }

bindingset[slug]
string routeName(string slug) {
  result = concat(string part, int i |
    part = slug.splitAt("-", i) and
    part.length() > 0
  |
    part.prefix(1).toUpperCase() + part.suffix(1), "" order by i
  )
}

predicate extendsNamed(ClassDefinition cls, string name) {
  name = cls.getSuperClass().(Identifier).getName()
  or
  cls.getSuperClass().toString() = name
}

predicate domainClientClass(ClassDefinition cls) {
  cls.getName().matches("%Client") and
  cls.getFile().getBaseName().matches("%-client.tsx") and
  exists(string slug | slug = moduleName(cls) and cls.getFile().getBaseName() = slug + "-client.tsx")
}

string domainClientId(ClassDefinition cls) {
  domainClientClass(cls) and
  result = dddNodeId("DomainClient", classFile(cls), cls.getName())
}

predicate domainNodeClass(ClassDefinition cls) {
  cls.getName().matches("%Node") and
  cls.getFile().getBaseName().matches("%-node.ts") and
  exists(string slug | slug = moduleName(cls) and cls.getFile().getBaseName() = slug + "-node.ts")
}

string domainNodeId(ClassDefinition cls) {
  domainNodeClass(cls) and
  result = dddNodeId("DomainNode", classFile(cls), cls.getName())
}

predicate jsonStoreFile(File file, string slug) {
  slug = fileSlash(file.getRelativePath()).regexpCapture("src/([^/]+)/[^/]+\\.json", 1) and
  file.getBaseName() = slug + ".json"
}

string jsonStoreId(File file) {
  exists(string slug | jsonStoreFile(file, slug) and result = dddNodeId("JsonStore", fileSlash(file.getRelativePath()), file.getBaseName()))
}

predicate routeFile(File file, string slug) {
  slug = fileSlash(file.getRelativePath()).regexpCapture("src/([^/]+)/[^/]+-routes\\.ts", 1) and
  file.getBaseName() = slug + "-routes.ts"
}

string routeId(File file) {
  exists(string slug |
    routeFile(file, slug) and
    result = dddNodeId("Route", fileSlash(file.getRelativePath()), routeName(slug))
  )
}

predicate destinationCall(MethodCallExpr call, string http, string path) {
  exists(File file |
    routeFile(file, _) and
    call.getFile() = file and
    http = call.getCalleeName() and
    http = ["get", "post", "put", "patch", "delete"] and
    path = call.getArgument(0).(StringLiteral).getValue() and
    path.matches("/%")
  )
}

bindingset[http, path]
string destinationName(string http, string path) { result = http.toUpperCase() + " " + path }

string destinationId(MethodCallExpr call) {
  exists(string http, string path |
    destinationCall(call, http, path) and
    result = dddNodeId("Destination", fileOf(call), destinationName(http, path))
  )
}

predicate domainView(Function func) {
  func.getName().matches("%View") and
  exists(string file |
    file = fileOf(func) and
    file.regexpMatch("src/[^/]+/[^/]+\\.tsx") and
    not file.matches("%-client\\.tsx")
  )
}

string domainViewId(Function func) {
  domainView(func) and
  result = dddNodeId("DomainView", fileOf(func), func.getName())
}

predicate entityKind(ClassDefinition cls, string kind, string id) {
  (kind = "Entity" or kind = "EntityRoot") and
  dddClass(cls, kind, id, _, _, _, _)
}

predicate rootOperation(string slug, MethodDefinition method) {
  exists(ClassDefinition cls |
    moduleName(cls) = slug and
    dddClass(cls, "EntityRoot", _, _, _, _, _) and
    method.getDeclaringType() = cls and
    method.getName() != "constructor"
  )
}

predicate repositoryVerb(string slug, MethodDefinition method) {
  exists(ClassDefinition cls |
    moduleName(cls) = slug and
    dddClass(cls, "Repository", _, _, _, _, _) and
    method.getDeclaringType() = cls and
    method.getName() = ["load", "create"]
  )
}

string operationNodeId(MethodDefinition method) {
  result =
    "clean_engineering:Operation:" + fileSlash(method.getFile().getRelativePath()) + ":" + method.getName() +
      ":" + method.getDeclaringType().getName()
}

predicate callUnder(AstNode outer, MethodCallExpr inner) {
  inner.getParent*() = outer and
  inner != outer
}

predicate specificFact(AstNode node, string id) {
  exists(ClassDefinition cls |
    cls = node and
    (
      id = domainClientId(cls) or
      id = domainNodeId(cls) or
      id = dddClassId(cls)
    )
  )
  or
  exists(Function func | func = node and id = domainViewId(func))
  or
  exists(MethodCallExpr call | call = node and id = destinationId(call))
}

string dddClassId(ClassDefinition cls) {
  exists(string kind | dddClass(cls, kind, result, _, _, _, _) and not domainClientClass(cls) and not domainNodeClass(cls))
}

string factId(AstNode node) {
  exists(string id | specificFact(node, id) and result = id)
  or
  not exists(string id | specificFact(node, id)) and
  result = "ddd:Entity:" + fileOf(node) + ":" + node.getLocation().getStartLine().toString()
}
