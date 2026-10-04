/**
 * @name examples-export-data-not-repository
 * @practice stories
 * @pattern lern_domain_driven
 * @fidelity acceptance_tests
 * @node module
 * @id stories/acceptance_tests/examples-export-data-not-repository
 */

import javascript
import subject_filter
import model

predicate exampleFile(File f) {
  f.getRelativePath().regexpMatch("(?i).*tests/.*/examples/.*\\.ts")
}

from AstNode node, string message, AstNode contributor
where
  exampleFile(node.getFile()) and
  inSubject(node) and
  (
    exists(ImportSpecifier spec, string repoName |
      spec = node and
      repoName = spec.getImportedName() and
      repoName.matches("%Repository") and
      not spec.getImportDeclaration().isTypeOnly() and
      contributor = spec and
      message =
        "Import production singleton '" + repoName +
          "' in examples/. Export field data or pass the repository from the story tier."
    )
    or
    exists(MethodCallExpr call, VarAccess receiver |
      call = node and
      receiver = call.getReceiver() and
      receiver.getName().matches("%Repository") and
      call.getMethodName() = ["new", "seed"] and
      contributor = call and
      message =
        "Call " + receiver.getName() + "." + call.getMethodName() +
          " in examples/. Export field data or a seed helper that takes the repository from the story."
    )
  )
select node, message, contributor
