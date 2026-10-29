/**
 * @name domain nodes
 * @kind problem
 * @id cdd/lern/ddd/nodes/domain-node
 */

import javascript
import lern

from ClassDefinition cls
where domainNodeClass(cls)
select domainNodeId(cls), cls.getName(), "DomainNode", "ddd", classFile(cls),
  cls.getLocation().getStartLine(), cls.getLocation().getEndLine(), "implementation"
