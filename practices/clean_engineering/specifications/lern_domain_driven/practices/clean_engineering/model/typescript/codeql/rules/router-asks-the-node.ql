/**
 * @name router-asks-the-node
 * @practice clean_engineering
 * @pattern lern_domain_driven
 * @fidelity code
 * @node method
 * @id clean_engineering/code/router-asks-the-node
 */

import javascript
import subject_filter
import model

from AstNode subject, string message, AstNode contributor
where
  exists(MethodDefinition destination, File f |
    inSubject(destination) and
    routerModuleFile(f) and
    destination.getFile() = f and
    destination.getName() = ["destination", "authDestination", "onboardingPath"] and
    subject = destination and
    contributor = destination and
    message =
      "The router only asks the node classes and returns the path they produce."
  )
  or
  exists(VarAccess step, File f |
    inSubject(step) and
    routerModuleFile(f) and
    step.getFile() = f and
    step.getName().matches("%Step") and
    subject = step and
    contributor = step and
    message =
      "The router only asks the node classes and returns the path they produce."
  )
  or
  exists(CallExpr repo |
    inSubject(repo) and
    (nodeFile(repo.getFile()) or serverFile(repo.getFile())) and
    repo.getCalleeName() = "load" and
    repo.toString().matches("repo.%") and
    subject = repo and
    contributor = repo and
    message = "Route handler calls repository directly - ask the node class instead."
  )
select subject, message, contributor
