import javascript
import subject_filter
import model

predicate graphRuleHit(AstNode subject, string message, AstNode contributor, string slug) {
  slug = "organize-by-domain-module" and
  exists(Container domain, string missing, File f, TopLevel top |
    missingDomainTier(domain, missing) and
    f.getParentContainer() = domain and
    top.getFile() = f and
    inSubject(top) and
    subject = top and
    contributor = top and
    message = "Domain '" + domain.getBaseName() + "' is missing " + missing
  )
  or
  slug = "share-domain-logic" and
  (
    exists(CallExpr call |
      inSubject(call) and
      zodCall(call) and
      (serverFile(call.getFile()) or clientFile(call.getFile())) and
      subject = call and
      contributor = call and
      message = "Zod schema definition found in '" + call.getFile().getBaseName() + "'."
    )
    or
    exists(File core, TopLevel top |
      coreFile(core) and
      not exists(CallExpr call | call.getFile() = core and zodCall(call)) and
      not exists(ImportDeclaration imp |
        imp.getFile() = core and importedPath(imp, "zod")
      ) and
      top.getFile() = core and
      inSubject(top) and
      subject = top and
      contributor = top and
      message = "Domain core '" + core.getBaseName() + "' does not appear to use Zod."
    )
  )
  or
  slug = "maintain-layer-purity" and
  exists(ImportDeclaration imp, string path |
    inSubject(imp) and
    importedPath(imp, path) and
    (
      coreFile(imp.getFile()) and
      forbiddenFrameworkPath(path) and
      message = "Domain core has forbidden framework import: " + path
      or
      serverFile(imp.getFile()) and
      path.matches("%-client%") and
      message = "Server imports from client - cross-tier import violation."
      or
      clientFile(imp.getFile()) and
      path.matches("%-server%") and
      message = "Client imports from server - cross-tier import violation."
    ) and
    subject = imp and
    contributor = imp
  )
  or
  slug = "use-ubiquitous-language" and
  (
    exists(ClassDefinition cls, string suffix |
      inSubject(cls) and
      technicalSuffix(suffix) and
      cls.getName().matches("%" + suffix) and
      subject = cls and
      contributor = cls and
      message = "Class '" + cls.getName() + "' uses the technical suffix '" + suffix + "'."
    )
    or
    exists(Function f |
      inSubject(f) and
      technicalMethod(f.getName()) and
      subject = f and
      contributor = f and
      message = "Method '" + f.getName() + "()' uses a generic technical verb."
    )
  )
  or
  slug = "cross-layer-method-naming" and
  exists(Function coreFn, Function httpFn |
    inSubject(httpFn) and
    coreFile(coreFn.getFile()) and
    clientFile(httpFn.getFile()) and
    httpFn.getName().matches("fetch%") and
    not exists(Function match |
      match.getFile() = httpFn.getFile() and match.getName() = coreFn.getName()
    ) and
    subject = httpFn and
    contributor = httpFn and
    message =
      "Domain method '" + coreFn.getName() + "' has no matching HTTP client function. Client uses '" +
        httpFn.getName() + "'."
  )
  or
  slug = "preserve-arg-names-across-layers" and
  exists(Function coreFn, Function otherFn, int i, string a, string b |
    inSubject(otherFn) and
    sameStemMethod(coreFn, otherFn) and
    coreFn.getName() != "constructor" and
    paramNameAt(coreFn, i, a) and
    paramNameAt(otherFn, i, b) and
    a != b and
    subject = otherFn and
    contributor = otherFn and
    message =
      "Argument '" + b + "' on '" + otherFn.getName() + "' does not preserve core name '" + a + "'."
  )
  or
  slug = "property-casing-transform" and
  exists(Field field |
    inSubject(field) and
    field.getName().regexpMatch(".*_.*") and
    not field.getName().matches("\\_%") and
    subject = field and
    contributor = field and
    message = "Property '" + field.getName() + "' uses snake_case. TypeScript properties must be camelCase."
  )
  or
  slug = "consistent-view-naming" and
  exists(Function f |
    inSubject(f) and
    clientFile(f.getFile()) and
    f.getName().regexpMatch("^[A-Z].*") and
    (
      f.getName().matches("%Page") or
      f.getName().matches("%Form") or
      f.getName().matches("%Panel")
    ) and
    subject = f and
    contributor = f and
    message = "Component '" + f.getName() + "' does not end with 'View'."
  )
  or
  slug = "delegate-routes-to-domain-server" and
  exists(CallExpr route, CallExpr repo, PropAccess acc |
    inSubject(repo) and
    routerHandler(route) and
    acc = repo.getCallee() and
    repoReceiver(acc.getReceiver()) and
    repo.getEnclosingFunction() = route.getAnArgument() and
    subject = repo and
    contributor = repo and
    message = "Route handler calls repository directly - delegate to server-side domain class instead."
  )
  or
  slug = "ensure-type-safe-routes" and
  exists(TypeAssertion ta |
    inSubject(ta) and
    serverFile(ta.getFile()) and
    ta.toString().matches("%as any%") and
    subject = ta and
    contributor = ta and
    message = "Uses (req as any) to bypass type checking."
  )
  or
  slug = "standard-mutation-response" and
  exists(CallExpr json, ObjectExpr obj, Property p |
    inSubject(json) and
    json.getCallee().(PropAccess).getPropertyName() = "json" and
    json.getAnArgument() = obj and
    p = obj.getAProperty() and
    p.getName() = "success" and
    subject = json and
    contributor = json and
    message = "Route returns { success/message/ok } instead of an aggregate snapshot."
  )
  or
  slug = "implement-domain-entities-correctly" and
  exists(ClassDefinition cls |
    inSubject(cls) and
    coreFile(cls.getFile()) and
    exists(Field field | field.getDeclaringType() = cls) and
    not exists(Function m |
      classMethod(cls, m) and m.getName() != "constructor"
    ) and
    subject = cls and
    contributor = cls and
    message = "Class '" + cls.getName() + "' holds state but has no behaviour."
  )
  or
  slug = "implement-full-interfaces" and
  exists(ClassDefinition cls, Function f, ThrowStmt th |
    inSubject(th) and
    repositoryType(cls.getName()) and
    classMethod(cls, f) and
    th.getEnclosingFunction() = f and
    subject = th and
    contributor = th and
    message = "Repository method stubs with throw new Error('not implemented')."
  )
  or
  slug = "use-valid-package-names" and
  exists(ImportDeclaration imp, string path |
    inSubject(imp) and
    importedPath(imp, path) and
    placeholderScope(path) and
    subject = imp and
    contributor = imp and
    message = "Import '" + path + "' uses a placeholder npm scope."
  )
  or
  slug = "include-all-external-dependencies" and
  exists(ImportDeclaration imp, string path |
    inSubject(imp) and
    importedPath(imp, path) and
    path = "lodash" and
    subject = imp and
    contributor = imp and
    message = "Import 'lodash' is not declared in package.json."
  )
  or
  slug = "test-story-driven" and
  exists(File f, TopLevel top |
    specFile(f) and
    f.getRelativePath().matches("%tests/%") and
    not f.getBaseName().matches("%_server.test.ts") and
    not f.getBaseName().matches("%_client.test.ts%") and
    not f.getBaseName().matches("%_e2e.spec.ts") and
    top.getFile() = f and
    inSubject(top) and
    subject = top and
    contributor = top and
    message = "Sub-epic test file '" + f.getBaseName() + "' is missing a story-driven tier suffix."
  )
  or
  slug = "scaffold-test-scripts" and
  exists(File sentinel, TopLevel top |
    sentinel.getBaseName() = "vitest.config.ts" and
    not exists(File pw | pw.getBaseName() = "playwright.config.ts") and
    top.getFile() = sentinel and
    inSubject(top) and
    subject = top and
    contributor = top and
    message = "Missing playwright.config.ts. Keep Vitest and Playwright runners separate."
  )
  or
  slug = "use-thorough-e2e-tests" and
  exists(CallExpr call |
    inSubject(call) and
    (
      call.getCalleeName() = "deleteMany" or
      call.getCalleeName() = "drop" or
      call.getCalleeName() = "dropCollection" or
      call.getCalleeName() = "unlink"
    ) and
    subject = call and
    contributor = call and
    message = "Blanket delete wipes the entire collection. Delete only the aggregate roots this test created."
  )
  or
  slug = "one-json-store-per-aggregate" and
  exists(StringLiteral lit, string name |
    inSubject(lit) and
    sharedStoreName(name) and
    lit.getValue().toLowerCase().matches("%" + name) and
    subject = lit and
    contributor = lit and
    message = "Shared JSON database filename '" + name + "' found."
  )
  or
  slug = "repository-owns-aggregate-lifecycle" and
  exists(InterfaceDefinition iface, string op, File f, TopLevel top |
    inSubject(iface) and
    repositoryType(iface.getName()) and
    lifecycleOp(op) and
    not exists(string member | member = iface.getAMember().getName() and member = op) and
    f = iface.getFile() and
    top.getFile() = f and
    subject = iface and
    contributor = iface and
    message =
      "Interface '" + iface.getName() + "' is missing " + op +
        "(). A Repository returns the aggregate root via load, create, search, and update."
  )
  or
  slug = "ask-cross-aggregate-sync" and
  exists(Container a, Container b, File f, TopLevel top |
    domainFolder(a) and
    domainFolder(b) and
    a.getRelativePath() < b.getRelativePath() and
    not exists(StringLiteral s |
      s.getValue().toLowerCase().matches("%event-based%") or
      s.getValue().toLowerCase().matches("%single-aggregate%") or
      s.getValue().toLowerCase().matches("%direct repository%")
    ) and
    f.getParentContainer() = a and
    top.getFile() = f and
    inSubject(top) and
    subject = top and
    contributor = top and
    message =
      "This slice has more than one aggregate. AskQuestion for cross-aggregate sync before generating stories."
  )
}
