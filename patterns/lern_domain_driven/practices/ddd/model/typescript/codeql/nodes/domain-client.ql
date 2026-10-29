/**
 * @name domain clients
 * @kind problem
 * @id cdd/lern/ddd/nodes/domain-client
 */

import javascript
import lern

from ClassDefinition cls
where domainClientClass(cls)
select domainClientId(cls), cls.getName(), "DomainClient", "ddd", classFile(cls),
  cls.getLocation().getStartLine(), cls.getLocation().getEndLine(), "implementation"
