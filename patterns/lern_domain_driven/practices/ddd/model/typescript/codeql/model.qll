import javascript
import ddd

predicate inGraphSubject(AstNode n) { exists(n.getLocation()) }

predicate nodeFile(File f) { f.getBaseName().matches("%-node.ts") }

predicate serverFile(File f) { f.getBaseName().matches("%-server.ts") }

predicate clientFile(File f) {
  f.getBaseName().matches("%-client.tsx") or f.getBaseName().matches("%-client.ts")
}

predicate tierFile(File f) { nodeFile(f) or serverFile(f) or clientFile(f) }

predicate srcAggregateFolder(Container folder) {
  folder.getParentContainer().getParentContainer().getParentContainer().getBaseName() = "src"
}

predicate srcCoreFile(File f) {
  f.getExtension() = "ts" and
  not f.getBaseName().matches("%-node.ts") and
  not f.getBaseName().matches("%-server.ts") and
  not f.getBaseName().matches("%-client.ts") and
  not f.getBaseName().matches("%-routes.ts") and
  (
    srcAggregateFolder(f.getParentContainer())
    or
    f.getParentContainer().getParentContainer().getBaseName() = "src"
  )
}

predicate coreFile(File f) {
  f.getExtension() = "ts" and
  not tierFile(f) and
  not f.getBaseName().matches("%.test.ts") and
  not f.getBaseName().matches("%.spec.ts") and
  not f.getBaseName() = "index.ts" and
  not f.getBaseName() = "app.ts" and
  not f.getBaseName() = "serve.ts" and
  (
    srcCoreFile(f)
    or
    exists(Container domain |
      domain = f.getParentContainer() and
      exists(File sibling | sibling.getParentContainer() = domain and tierFile(sibling))
    )
  )
}

predicate domainFolder(Container domain) {
  exists(File f |
    f.getParentContainer() = domain and
    (coreFile(f) or tierFile(f))
  )
}

predicate importedPath(ImportDeclaration imp, string path) {
  path = imp.getImportedPathString()
}

bindingset[path]
predicate forbiddenFrameworkPath(string path) {
  path = "express" or
  path = "react" or
  path = "react-dom" or
  path = "lowdb" or
  path.matches("lowdb/%") or
  path.matches("@tanstack%") or
  path = "zustand" or
  path = "redux" or
  path.matches("@reduxjs%")
}

predicate technicalSuffix(string suffix) {
  suffix = "Manager" or
  suffix = "Handler" or
  suffix = "Processor" or
  suffix = "Helper" or
  suffix = "Utility" or
  suffix = "Utils" or
  suffix = "Util" or
  suffix = "Builder" or
  suffix = "Factory" or
  suffix = "Provider"
}

predicate technicalMethod(string name) {
  name = "process" or
  name = "handle" or
  name = "execute" or
  name = "run" or
  name = "manage" or
  name = "perform" or
  name = "doWork" or
  name = "doTask" or
  name = "doAction"
}

predicate lifecycleOp(string name) {
  name = "load" or name = "create" or name = "search" or name = "update"
}

bindingset[name]
predicate repositoryType(string name) { name.matches("%Repository") }

predicate zodCall(CallExpr call) {
  call.getCalleeName() = "object" or
  call.getCalleeName() = "string" or
  call.getCalleeName() = "enum" or
  call.getCalleeName() = "array"
}

predicate sharedStoreName(string name) {
  name = "db.json" or name = "database.json" or name = "store.json" or name = "data.json"
}

predicate routerHandler(CallExpr call) {
  call.getCalleeName() = "get" or
  call.getCalleeName() = "post" or
  call.getCalleeName() = "put" or
  call.getCalleeName() = "patch" or
  call.getCalleeName() = "delete"
}

bindingset[name]
predicate placeholderScope(string name) {
  name.matches("@example/%") or
  name.matches("@project/%") or
  name.matches("@acme/%") or
  name.matches("@app/%") or
  name.matches("@myapp/%") or
  name.matches("@todo/%") or
  name.matches("@sample/%") or
  name.matches("@demo/%")
}

predicate specFile(File f) {
  f.getBaseName().matches("%.test.ts") or
  f.getBaseName().matches("%.test.tsx") or
  f.getBaseName().matches("%.spec.ts") or
  f.getBaseName().matches("%.spec.tsx")
}

bindingset[path]
predicate epicPackagePath(string path) {
  path.regexpMatch("packages/[^/]+/.+")
}

predicate routeFile(File f) { f.getBaseName().matches("%-routes.ts") }

predicate routerModuleFile(File f) {
  routeFile(f) and srcAggregateFolder(f.getParentContainer())
}

predicate screenViewFile(File f) {
  f.getExtension() = "tsx" and
  not clientFile(f) and
  not f.getBaseName().matches("%-redirect.tsx") and
  not f.getBaseName().matches("%-shell.tsx") and
  srcAggregateFolder(f.getParentContainer())
}

bindingset[slug]
string pascalFromSlug(string slug) {
  result = concat(string part, int i |
    part = slug.splitAt("-", i) and
    part.length() > 0
  |
    part.prefix(1).toUpperCase() + part.suffix(1), "" order by i
  )
}

string domainSlugFromClient(ClassDefinition cls) {
  result =
    slash(cls.getFile().getRelativePath()).regexpCapture("src/(?:[^/]+/)?([^/]+)/[^/]+-client\\.(tsx|ts)$", 1)
}

predicate domainClient(
  ClassDefinition cls, string id, string name, string file, int start, int end
) {
  clientFile(cls.getFile()) and
  cls.getName().regexpMatch(".+Client") and
  name = cls.getName() and
  file = slash(cls.getFile().getRelativePath()) and
  start = cls.getLocation().getStartLine() and
  end = cls.getLocation().getEndLine() and
  id = "ddd:DomainClient:" + file + ":" + name
}

predicate domainNode(
  ClassDefinition cls, string id, string name, string file, int start, int end
) {
  nodeFile(cls.getFile()) and
  cls.getName().regexpMatch(".+Node") and
  name = cls.getName() and
  file = slash(cls.getFile().getRelativePath()) and
  start = cls.getLocation().getStartLine() and
  end = cls.getLocation().getEndLine() and
  id = "ddd:DomainNode:" + file + ":" + name
}

predicate domainView(
  File f, string id, string name, string file, int start, int end
) {
  screenViewFile(f) and
  name = f.getBaseName().regexpCapture("^(.+)\\.tsx$", 1) and
  file = slash(f.getRelativePath()) and
  start = f.getLocation().getStartLine() and
  end = f.getLocation().getEndLine() and
  id = "ddd:DomainView:" + file + ":" + name
}

predicate jsonStore(File f, string id, string name, string file) {
  f.getExtension() = "json" and
  srcAggregateFolder(f.getParentContainer()) and
  name = f.getBaseName().regexpCapture("^(.+)\\.json$", 1) and
  file = slash(f.getRelativePath()) and
  id = "ddd:JsonStore:" + file + ":" + name
}

predicate routeModule(File f, string id, string name, string file, int start, int end) {
  routeFile(f) and
  srcAggregateFolder(f.getParentContainer()) and
  name = f.getBaseName().regexpCapture("^(.+)-routes\\.ts$", 1) and
  file = slash(f.getRelativePath()) and
  start = f.getLocation().getStartLine() and
  end = f.getLocation().getEndLine() and
  id = "ddd:Route:" + file + ":" + name
}

predicate clientInteractsEntityEdge(string parent, string child) {
  exists(
    ClassDefinition clientCls, ClassDefinition rootCls, string parentId, string childId,
    string clientClassName, string clientPath, int clientStartLine, int clientEndLine,
    string rootClassName, string rootPath, int rootStartLine, int rootEndLine
  |
    domainClient(clientCls, parentId, clientClassName, clientPath, clientStartLine, clientEndLine) and
    parent = parentId and
    dddClass(
      rootCls, "EntityRoot", childId, rootClassName, rootPath, rootStartLine, rootEndLine
    ) and
    child = childId and
    clientCls.getFile().getParentContainer() = rootCls.getFile().getParentContainer()
  )
}

predicate nodeHostsEntityEdge(string parent, string child) {
  exists(
    ClassDefinition nodeCls, ClassDefinition rootCls, string parentId, string childId,
    string nodeClassName, string nodePath, int nodeStartLine, int nodeEndLine,
    string rootClassName, string rootPath, int rootStartLine, int rootEndLine
  |
    domainNode(nodeCls, parentId, nodeClassName, nodePath, nodeStartLine, nodeEndLine) and
    parent = parentId and
    dddClass(
      rootCls, "EntityRoot", childId, rootClassName, rootPath, rootStartLine, rootEndLine
    ) and
    child = childId and
    nodeCls.getFile().getParentContainer() = rootCls.getFile().getParentContainer()
  )
}

