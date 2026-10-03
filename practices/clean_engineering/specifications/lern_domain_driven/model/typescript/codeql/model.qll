import javascript
import subject_filter

predicate serverFile(File f) { f.getBaseName().matches("%-server.ts") }

predicate clientFile(File f) {
  f.getBaseName().matches("%-client.tsx") or f.getBaseName().matches("%-client.ts")
}

predicate coreFile(File f) {
  f.getExtension() = "ts" and
  not serverFile(f) and
  not clientFile(f) and
  not f.getBaseName().matches("%.test.ts") and
  not f.getBaseName().matches("%.spec.ts") and
  not f.getBaseName() = "index.ts" and
  not f.getBaseName() = "app.ts" and
  not f.getBaseName() = "serve.ts" and
  exists(Container domain |
    domain = f.getParentContainer() and
    (
      exists(File sibling | sibling.getParentContainer() = domain and serverFile(sibling)) or
      exists(File sibling | sibling.getParentContainer() = domain and clientFile(sibling))
    )
  )
}

predicate domainFolder(Container domain) {
  exists(File f |
    f.getParentContainer() = domain and
    (coreFile(f) or serverFile(f) or clientFile(f))
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

predicate missingDomainTier(Container domain, string missing) {
  domainFolder(domain) and
  (
    not exists(File f | f.getParentContainer() = domain and coreFile(f)) and
    missing = domain.getBaseName() + ".ts"
    or
    not exists(File f | f.getParentContainer() = domain and serverFile(f)) and
    missing = "*-server.ts"
    or
    not exists(File f | f.getParentContainer() = domain and clientFile(f)) and
    missing = "*-client.tsx"
  )
}
