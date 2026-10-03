/**
 * @name views-render-only
 * @practice clean_engineering
 * @pattern lern_domain_driven
 * @fidelity code
 * @node function
 * @id clean_engineering/code/views-render-only
 */

import javascript
import subject_filter
import model

from AstNode subject, string message, AstNode contributor
where
  exists(FunctionDeclStmt fn, File f |
    inSubject(fn) and
    screenViewFile(f) and
    fn.getFile() = f and
    fn.getName() = ["destination", "authDestination", "onboardingPath", "requirementLines"] and
    subject = fn and
    contributor = fn.getIdentifier() and
    message =
      "A screen view only renders. Field entry, host operations, and the next page stay on the client subtype or the node class."
  )
  or
  exists(MethodDefinition method, File f |
    inSubject(method) and
    screenViewFile(f) and
    method.getFile() = f and
    method.getName() = ["destination", "authDestination", "onboardingPath", "requirementLines"] and
    subject = method and
    contributor = method.getDeclaringClass() and
    message =
      "A screen view only renders. Field entry, host operations, and the next page stay on the client subtype or the node class."
  )
select subject, message, contributor
