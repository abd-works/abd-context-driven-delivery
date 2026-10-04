/**
 * @name use-ctx-repository-directly
 * @practice ddd
 * @pattern lern_domain_driven
 * @fidelity tactics
 * @node module
 * @id ddd/tactics/use-ctx-repository-directly
 */

import javascript
import subject_filter
import model

predicate storyStepFile(File file) {
  file.getBaseName().regexpMatch(".*\\.story\\.(shared|domain\\.spec|server\\.spec)\\.ts")
}

predicate ctxRepositoryAccess(PropAccess access) {
  access.getPropertyName().matches("%Repository") and
  access.getBase().(VarAccess).getName() = "ctx"
}

from AstNode subject, string message, AstNode contributor
where
  storyStepFile(subject.getFile()) and
  inSubject(subject) and
  (
    exists(TypeAssertion assertion, PropAccess access |
      subject = assertion and
      access = assertion.getExpression() and
      ctxRepositoryAccess(access) and
      contributor = access and
      message =
        "Use ctx." + access.getPropertyName() + " directly. Do not cast the ctx binding."
    )
    or
    exists(Function fn, ReturnStmt ret, PropAccess access |
      subject = fn and
      fn.getName().matches("%Repository") and
      ret.getContainer() = fn and
      (
        access = ret.getExpr() or
        access = ret.getExpr().(TypeAssertion).getExpression()
      ) and
      ctxRepositoryAccess(access) and
      contributor = access and
      message =
        "Use ctx." + fn.getName() + " in the step. Do not wrap the ctx binding in a function."
    )
  )
select subject, message, contributor
