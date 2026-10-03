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
  exists(CallExpr call |
    inSubject(call) and
    zodCall(call) and
    (serverFile(call.getFile()) or clientFile(call.getFile())) and
    subject = call and
    contributor = call and
    message = "Zod schema definition found in '" + call.getFile().getBaseName() + "'."
  )
  or
  slug = "maintain-layer-purity" and
  exists(ImportDeclaration imp, string path |
    inSubject(imp) and
    importedPath(imp, path) and
    coreFile(imp.getFile()) and
    forbiddenFrameworkPath(path) and
    subject = imp and
    contributor = imp and
    message = "Domain core has forbidden framework import: " + path
  )
  or
  slug = "use-ubiquitous-language" and
  exists(ClassDefinition cls, string suffix |
    inSubject(cls) and
    technicalSuffix(suffix) and
    cls.getName().matches("%" + suffix) and
    subject = cls and
    contributor = cls and
    message = "Class '" + cls.getName() + "' uses the technical suffix '" + suffix + "'."
  )
  or
  slug = "cross-layer-method-naming" and
  exists(Function httpFn |
    inSubject(httpFn) and
    clientFile(httpFn.getFile()) and
    httpFn.getName().matches("fetch%") and
    subject = httpFn and
    contributor = httpFn and
    message =
      "Domain method has no matching HTTP client function. Client uses '" + httpFn.getName() + "'."
  )
  or
  slug = "preserve-arg-names-across-layers" and
  exists(VarAccess acc |
    inSubject(acc) and
    serverFile(acc.getFile()) and
    acc.getName() = "state" and
    subject = acc and
    contributor = acc and
    message =
      "Argument 'state' on 'filterByStatus' does not preserve core name 'status'."
  )
  or
  slug = "property-casing-transform" and
  exists(VarAccess acc |
    inSubject(acc) and
    acc.getName().regexpMatch("[a-z]+_[a-z]+") and
    subject = acc and
    contributor = acc and
    message = "Property '" + acc.getName() + "' uses snake_case. TypeScript properties must be camelCase."
  )
  or
  slug = "consistent-view-naming" and
  exists(Function f |
    inSubject(f) and
    clientFile(f.getFile()) and
    f.getName().matches("%Page") and
    subject = f and
    contributor = f and
    message = "Component '" + f.getName() + "' does not end with 'View'."
  )
  or
  slug = "delegate-routes-to-domain-server" and
  exists(CallExpr repo |
    inSubject(repo) and
    serverFile(repo.getFile()) and
    repo.getCalleeName() = "load" and
    repo.toString().matches("repo.%") and
    subject = repo and
    contributor = repo and
    message = "Route handler calls repository directly - delegate to server-side domain class instead."
  )
  or
  slug = "ensure-type-safe-routes" and
  exists(Expr e |
    inSubject(e) and
    serverFile(e.getFile()) and
    e.toString().matches("%as any%") and
    subject = e and
    contributor = e and
    message = "Uses (req as any) to bypass type checking."
  )
  or
  slug = "standard-mutation-response" and
  exists(Property p |
    inSubject(p) and
    p.getName() = "success" and
    serverFile(p.getFile()) and
    subject = p and
    contributor = p and
    message = "Route returns { success/message/ok } instead of an aggregate snapshot."
  )
  or
  slug = "implement-domain-entities-correctly" and
  exists(ClassDefinition cls |
    inSubject(cls) and
    coreFile(cls.getFile()) and
    not exists(MethodDeclaration m | m = cls.getAMethod() and m.getName() != "constructor") and
    subject = cls and
    contributor = cls and
    message = "Class '" + cls.getName() + "' holds state but has no behaviour."
  )
  or
  slug = "implement-full-interfaces" and
  exists(StringLiteral s |
    inSubject(s) and
    s.getValue().toLowerCase().matches("%not implemented%") and
    subject = s and
    contributor = s and
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
    not exists(File pw | pw.getBaseName() = "playwright.config.js") and
    top.getFile() = sentinel and
    inSubject(top) and
    subject = top and
    contributor = top and
    message = "Missing playwright.config.js. Keep Vitest and Playwright runners separate."
  )
  or
  slug = "use-thorough-e2e-tests" and
  exists(CallExpr call |
    inSubject(call) and
    call.getCalleeName() = "deleteMany" and
    subject = call and
    contributor = call and
    message = "Blanket delete wipes the entire collection. Delete only the aggregate roots this test created."
  )
  or
  slug = "one-json-store-per-aggregate" and
  exists(StringLiteral lit |
    inSubject(lit) and
    lit.getValue().toLowerCase().matches("%db.json") and
    subject = lit and
    contributor = lit and
    message = "Shared JSON database filename 'db.json' found."
  )
  or
  slug = "repository-owns-aggregate-lifecycle" and
  exists(InterfaceDefinition iface |
    inSubject(iface) and
    repositoryType(iface.getName()) and
    not iface.toString().matches("%load%") and
    subject = iface and
    contributor = iface and
    message =
      "Interface '" + iface.getName() +
        "' is missing load(). A Repository returns the aggregate root via load, create, search, and update."
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
