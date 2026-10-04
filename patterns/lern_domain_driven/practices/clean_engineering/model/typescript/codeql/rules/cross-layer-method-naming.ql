/**
 * @name cross-layer-method-naming
 * @practice clean_engineering
 * @pattern lern_domain_driven
 * @fidelity model
 * @node function
 * @id clean_engineering/model/cross-layer-method-naming
 */

import javascript
import subject_filter
import model

from AstNode subject, string message, AstNode contributor
where
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
  exists(Function coreFn, Function hostFn, Parameter coreP, Parameter hostP, int i |
    inSubject(hostFn) and
    coreFile(coreFn.getFile()) and
    (
      nodeFile(hostFn.getFile()) or
      serverFile(hostFn.getFile()) or
      clientFile(hostFn.getFile())
    ) and
    coreFn.getFile().getParentContainer() = hostFn.getFile().getParentContainer() and
    coreFn.getName() = hostFn.getName() and
    coreFn.getName() != "constructor" and
    coreP = coreFn.getParameter(i) and
    hostP = hostFn.getParameter(i) and
    coreP.getName() != hostP.getName() and
    subject = hostP and
    contributor = hostP and
    message =
      "Argument '" + hostP.getName() + "' on '" + hostFn.getName() +
        "' does not preserve core name '" + coreP.getName() + "'."
  )
select subject, message, contributor
