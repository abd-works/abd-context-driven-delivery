/**
 * @name share-domain-logic
 * @practice clean_engineering
 * @pattern lern_domain_driven
 * @fidelity model
 * @node class
 * @id clean_engineering/model/share-domain-logic
 */

import javascript
import subject_filter
import model

predicate zodInHost(CallExpr call) {
  zodCall(call) and
  (
    nodeFile(call.getFile()) or
    serverFile(call.getFile()) or
    clientFile(call.getFile())
  )
}

predicate frameworkInCore(ImportDeclaration imp, string path) {
  importedPath(imp, path) and
  coreFile(imp.getFile()) and
  forbiddenFrameworkPath(path)
}

predicate hostCrossImport(ImportDeclaration imp, string path) {
  importedPath(imp, path) and
  (
    clientFile(imp.getFile()) and
    (path.matches("%-node") or path.matches("%-server"))
    or
    (nodeFile(imp.getFile()) or serverFile(imp.getFile())) and
    path.matches("%-client")
  )
}

from AstNode subject, string message, AstNode contributor
where
  exists(CallExpr call |
    inSubject(call) and
    zodInHost(call) and
    subject = call and
    contributor = call and
    message = "Zod schema definition found in '" + call.getFile().getBaseName() + "'."
  )
  or
  exists(ImportDeclaration imp, string path |
    inSubject(imp) and
    frameworkInCore(imp, path) and
    subject = imp and
    contributor = imp and
    message = "Domain core has forbidden framework import: " + path
  )
  or
  exists(ImportDeclaration imp, string path |
    inSubject(imp) and
    hostCrossImport(imp, path) and
    subject = imp and
    contributor = imp and
    message =
      "Host '" + imp.getFile().getBaseName() +
        "' imports '" + path + "'. Client and node never cross-import; both import the domain file."
  )
select subject, message, contributor
