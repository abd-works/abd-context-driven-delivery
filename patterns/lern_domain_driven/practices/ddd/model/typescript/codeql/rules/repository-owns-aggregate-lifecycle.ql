/**
 * @name repository-owns-aggregate-lifecycle
 * @practice ddd
 * @pattern lern_domain_driven
 * @fidelity tactics
 * @node class
 * @id ddd/tactics/repository-owns-aggregate-lifecycle
 */

import javascript
import subject_filter
import model

from AstNode subject, string message, AstNode contributor
where
  exists(InterfaceDefinition iface |
    inSubject(iface) and
    repositoryType(iface.getName()) and
    not exists(Function loadFn |
      loadFn.getName() = "load" and
      loadFn.getFile() = iface.getFile()
    ) and
    subject = iface and
    contributor = iface and
    message =
      "Interface '" + iface.getName() +
        "' is missing load(). A Repository returns the aggregate root via load, create, search, and update."
  )
  or
  exists(MethodDefinition method |
    inSubject(method) and
    repositoryType(method.getDeclaringType().getName()) and
    method.getName() = ["rehydrate", "hydrate"] and
    subject = method and
    contributor = method and
    message =
      method.getDeclaringType().getName() + "." + method.getName() +
        " is not a collection operation. Reconstruct the aggregate inside load (and create, search, update)."
  )
select subject, message, contributor
