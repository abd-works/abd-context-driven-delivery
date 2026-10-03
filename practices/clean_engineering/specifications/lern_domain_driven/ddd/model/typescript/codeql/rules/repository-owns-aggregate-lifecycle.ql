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

from InterfaceDefinition iface, string message, AstNode contributor
where
  inSubject(iface) and
  repositoryType(iface.getName()) and
  not iface.toString().matches("%load%") and
  message =
    "Interface '" + iface.getName() +
      "' is missing load(). A Repository returns the aggregate root via load, create, search, and update." and
  contributor = iface
select iface, message, contributor
