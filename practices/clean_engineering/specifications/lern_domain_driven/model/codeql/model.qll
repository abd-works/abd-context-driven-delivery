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
  exists(File f | f.getParentContainer() = domain and (coreFile(f) or serverFile(f) or clientFile(f)))
}

predicate domainName(Container domain, string name) { name = domain.getBaseName() }

predicate importedPath(ImportDeclaration imp, string path) { path = imp.getImportedPathString() }

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

predicate repositoryType(string name) { name.matches("%Repository") }

predicate zodCall(CallExpr call) {
  exists(PropAccess acc |
    acc = call.getCallee() and
    (
      acc.getPropertyName() = "object" or
      acc.getPropertyName() = "string" or
      acc.getPropertyName() = "number" or
      acc.getPropertyName() = "boolean" or
      acc.getPropertyName() = "enum" or
      acc.getPropertyName() = "array" or
      acc.getPropertyName() = "union"
    )
  )
}

predicate parseCall(CallExpr call) {
  exists(PropAccess acc |
    acc = call.getCallee() and
    (acc.getPropertyName() = "parse" or acc.getPropertyName() = "safeParse")
  )
}

predicate schemaName(string name) { name.matches("%Schema") }

predicate usesSchemaName(File f) {
  exists(VarAccess acc | acc.getFile() = f and schemaName(acc.getName()))
}

predicate sharedStoreName(string name) {
  name = "db.json" or name = "database.json" or name = "store.json" or name = "data.json"
}

predicate jsonPresetCall(CallExpr call) {
  call.getCalleeName().matches("JSONFile%") or call.getCalleeName().matches("%Preset")
}

predicate routerHandler(CallExpr call) {
  exists(PropAccess acc |
    acc = call.getCallee() and
    acc.getReceiver().(VarAccess).getName() = "router" and
    (
      acc.getPropertyName() = "get" or
      acc.getPropertyName() = "post" or
      acc.getPropertyName() = "put" or
      acc.getPropertyName() = "patch" or
      acc.getPropertyName() = "delete"
    )
  )
}

predicate repoReceiver(Expr recv) {
  recv.(VarAccess).getName() = "repo" or recv.(VarAccess).getName() = "repository"
}

predicate methodNamed(Function f, string name) { name = f.getName() }

predicate classMethod(ClassDefinition cls, Function method) { method = cls.getAMethod() }

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

predicate nodeBuiltin(string name) {
  name = "path" or
  name = "fs" or
  name = "os" or
  name = "crypto" or
  name = "util" or
  name = "events" or
  name = "stream" or
  name = "http" or
  name = "https" or
  name = "url" or
  name = "buffer" or
  name = "process" or
  name = "module"
}

predicate relativeOrAlias(string path) {
  path.matches("./%") or path.matches("../%") or path.matches("@/%")
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

predicate sameStemMethod(Function coreFn, Function otherFn) {
  coreFn.getName() = otherFn.getName() and
  coreFile(coreFn.getFile()) and
  (serverFile(otherFn.getFile()) or clientFile(otherFn.getFile()))
}

predicate paramNameAt(Function f, int i, string name) { name = f.getParameter(i).getName() }
