/**
 * @name ask-cross-aggregate-sync
 * @practice ddd
 * @pattern lern_domain_driven
 * @fidelity building_blocks
 * @node module
 * @id ddd/building_blocks/ask-cross-aggregate-sync
 */

import javascript
import subject_filter
import model

predicate fileSrcDomain(File f, string domain) {
  f.getParentContainer().getParentContainer().getBaseName() = "src" and
  domain = f.getParentContainer().getBaseName() and
  domain != "systems"
}

predicate srcDomainImport(ImportDeclaration imp, string domain) {
  exists(string path |
    importedPath(imp, path) and
    (
      domain = path.regexpCapture("(?i)(?:^|/)src/([^/]+)/.*", 1)
      or
      domain = path.regexpCapture("(?i)@src/([^/]+)/.*", 1)
      or
      domain = path.regexpCapture("(?i)\\.\\./([^/]+)/.*", 1)
    ) and
    domain != "systems"
  )
}

from ImportDeclaration imp, string home, string other, string message, AstNode contributor
where
  fileSrcDomain(imp.getFile(), home) and
  srcDomainImport(imp, other) and
  other != home and
  not nodeFile(imp.getFile()) and
  not clientFile(imp.getFile()) and
  not specFile(imp.getFile()) and
  inSubject(imp) and
  not exists(File note |
    note.getBaseName().regexpMatch("(?i).*sync.*") and
    (
      note.getParentContainer() = imp.getFile().getParentContainer() or
      note.getParentContainer() = imp.getFile().getParentContainer().getParentContainer()
    )
  ) and
  message =
    "This file uses aggregates '" + home + "' and '" + other +
      "'. AskQuestion for cross-aggregate sync before generating stories." and
  contributor = imp
select imp, message, contributor
