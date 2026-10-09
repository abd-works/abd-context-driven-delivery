/**
 * @name domain-core-file-matches-folder-slug
 * @practice clean_engineering
 * @pattern lern_domain_driven
 * @fidelity model
 * @node module
 * @id clean_engineering/model/domain-core-file-matches-folder-slug
 */

import javascript
import subject_filter
import model

predicate srcDomainFolder(Container domain, string slug) {
  aggregateFolder(domain) and
  slug = domain.getBaseName() and
  exists(File f | f.getParentContainer() = domain)
}

predicate hasKebabCore(Container domain, string slug) {
  exists(File f |
    f.getParentContainer() = domain and
    f.getBaseName() = slug + ".ts"
  )
}

predicate hasClient(Container domain, string slug) {
  exists(File f |
    f.getParentContainer() = domain and
    f.getBaseName() = slug + "-client.tsx"
  )
}

predicate hasNode(Container domain, string slug) {
  exists(File f |
    f.getParentContainer() = domain and
    f.getBaseName() = slug + "-node.ts"
  )
}

from AstNode subject, string message, AstNode contributor
where
  exists(File core, TopLevel top |
    core = top.getFile() and
    inSubject(top) and
    core.getRelativePath().regexpMatch("src/(?:[^/]+/){1,2}[A-Z][A-Za-z0-9]*\\.ts") and
    not core.getRelativePath().regexpMatch("src/systems/.*") and
    core.getBaseName() =
      pascalFromSlug(core.getParentContainer().getBaseName()) + ".ts" and
    subject = top and
    contributor = top and
    message =
      "Domain core file must match the folder slug in kebab-case (for example customer/customer.ts)."
  )
  or
  exists(File file, TopLevel top |
    file = top.getFile() and
    inSubject(top) and
    file.getRelativePath().regexpMatch("src/(?:[^/]+/){1,2}[^/]+-server\\.ts$") and
    subject = top and
    contributor = top and
    message = "Node tier file must use <domain>-node.ts, not -server.ts."
  )
  or
  exists(ClassDefinition cls |
    inSubject(cls) and
    cls.getName().matches("%Server") and
    cls.getFile().getRelativePath().regexpMatch("src/(?:[^/]+/){1,2}[^/]+\\.(ts|tsx)$") and
    subject = cls and
    contributor = cls and
    message =
      "Node tier class " + cls.getName() +
        " must use the Node suffix (for example CustomerNode), not Server."
  )
  or
  exists(Container domain, string slug, TopLevel top |
    srcDomainFolder(domain, slug) and
    (hasKebabCore(domain, slug) or hasClient(domain, slug) or hasNode(domain, slug)) and
    (
      not hasKebabCore(domain, slug) or
      not hasClient(domain, slug) or
      not hasNode(domain, slug)
    ) and
    top.getFile().getParentContainer() = domain and
    inSubject(top) and
    subject = top and
    contributor = top and
    message =
      "Aggregate src/<bounded context>/" + slug + "/ holds " + slug + ".ts, " + slug +
        "-client.tsx, " + slug + "-node.ts, its views, and one route file."
  )
  or
  exists(ClassDefinition cls, string folderSlug, string domainName |
    inSubject(cls) and
    folderSlug = cls.getFile().getParentContainer().getBaseName() and
    (
      aggregateFolder(cls.getFile().getParentContainer()) or
      cls.getFile().getParentContainer().getParentContainer().getBaseName() = "src"
    ) and
    domainName = pascalFromSlug(folderSlug) and
    (
      cls.getFile().getBaseName() = folderSlug + "-client.tsx" and
      cls.getName() = domainName + "Client"
      or
      cls.getFile().getBaseName() = folderSlug + "-node.ts" and
      cls.getName() = domainName + "Node"
    ) and
    not cls.getSuperClass().(VarAccess).getName() = domainName and
    subject = cls and
    contributor = cls.getIdentifier() and
    message =
      cls.getName() + " subtypes " + domainName +
        " declared in the domain file for this folder."
  )
  or
  exists(File artifact, TopLevel top |
    artifact = top.getFile() and
    inSubject(top) and
    epicPackagePath(artifact.getRelativePath()) and
    (
      artifact.getBaseName().matches("%-node.ts") or
      artifact.getBaseName().matches("%-server.ts") or
      artifact.getBaseName().matches("%-client.tsx") or
      (
        artifact.getExtension() = "tsx" and
        not artifact.getBaseName() = "main.tsx" and
        not artifact.getBaseName().matches("%-redirect.tsx") and
        not artifact.getBaseName().matches("%-shell.tsx") and
        not artifact.getBaseName().matches("%-view.tsx")
      ) or
      routeFile(artifact) or
      artifact.getRelativePath().regexpMatch("packages/[^/]+/data/[^/]+\\.json") or
      artifact.getRelativePath().regexpMatch("packages/[^/]+/.+/data/[^/]+\\.json") or
      artifact.getRelativePath().regexpMatch("packages/[^/]+/.+/source/[^/]+\\.ts") or
      artifact.getRelativePath().regexpMatch("packages/[^/]+/[^/]+/[^/]+\\.ts")
    ) and
    subject = top and
    contributor = top and
    message =
      "Domain tier '" + artifact.getRelativePath() +
        "' belongs in src/<bounded context>/<aggregate>/ with its views, node file, and client file, not inside packages/<epicSlug>/."
  )
  or
  exists(File flat, TopLevel top |
    flat = top.getFile() and
    inSubject(top) and
    flat.getParentContainer().getParentContainer().getBaseName() = "src" and
    not flat.getRelativePath().regexpMatch("src/systems/.*") and
    (
      flat.getExtension() = "ts" or
      flat.getExtension() = "tsx"
    ) and
    subject = top and
    contributor = top and
    message =
      "Aggregate files live in src/<bounded context>/<aggregate>/, with the views, the node file, and the client file."
  )
  or
  exists(Container folder, File route, TopLevel top |
    aggregateFolder(folder) and
    route.getParentContainer() = folder and
    routeFile(route) and
    count(File other | other.getParentContainer() = folder and routeFile(other)) > 1 and
    top.getFile() = route and
    inSubject(top) and
    subject = top and
    contributor = top and
    message = "An aggregate has one route file."
  )
  or
  exists(File view, ImportDeclaration imp, string path, TopLevel top |
    view.getExtension() = "tsx" and
    not clientFile(view) and
    top.getFile() = view and
    inSubject(top) and
    imp.getFile() = view and
    importedPath(imp, path) and
    path.regexpMatch(".*\\.\\./.*-(client|node)(\\.(tsx|ts))?$") and
    subject = top and
    contributor = imp and
    message =
      "A view, the client file, and the node file live in the same aggregate folder."
  )
  or
  exists(ImportDeclaration imp, string path |
    inSubject(imp) and
    importedPath(imp, path) and
    placeholderScope(path) and
    subject = imp and
    contributor = imp and
    message = "Import '" + path + "' uses a placeholder npm scope."
  )
select subject, message, contributor
