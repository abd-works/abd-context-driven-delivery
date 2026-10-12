/**
 * @name lern domain nodes
 * @kind problem
 * @id cdd/lern/ddd/domain-node
 */

import javascript
import model

from ClassDefinition cls, string id, string name, string file, int start, int end
where domainNode(cls, id, name, file, start, end)
select id, name, "DomainNode", "ddd", file, start, end,
  "clean_engineering:OoadClass:" + file + ":" + name, "true", "implementation"
