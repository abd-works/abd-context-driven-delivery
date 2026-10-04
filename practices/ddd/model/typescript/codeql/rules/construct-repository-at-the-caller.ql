/**
 * @name construct-repository-at-the-caller
 * @kind problem
 * @id paradise/construct-repository-at-the-caller
 * @problem.severity warning
 */

import javascript

predicate repositoryConstruction(NewExpr construction) {
  construction.getCalleeName().regexpMatch(".*Repository.*")
}

predicate moduleScope(AstNode node) { not exists(Function f | node.getParent*() = f) }

predicate nodeModule(File file) { file.getBaseName().regexpMatch(".*-node\\.ts") }

predicate storyOrTest(File file) { file.getRelativePath().regexpMatch(".*tests/.*") }

from VariableDeclarator decl, NewExpr construction, string message
where
  moduleScope(decl) and
  construction = decl.getInit() and
  repositoryConstruction(construction) and
  (
    nodeModule(decl.getFile()) and
    message =
      "The node module exports the class only. Production creates the repository in the route and passes it into destination. A test creates it in the scenario."
    or
    storyOrTest(decl.getFile()) and
    message =
      "Create new Repository() in the scenario that needs it. Do not construct a repository at module scope."
  )
select decl, message, construction
