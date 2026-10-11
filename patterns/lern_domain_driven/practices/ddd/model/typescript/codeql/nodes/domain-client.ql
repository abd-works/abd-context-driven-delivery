/**
 * @name lern domain clients
 * @kind problem
 * @id cdd/lern/ddd/domain-client
 */

import javascript
import model

from ClassDefinition cls, string id, string name, string file, int start, int end
where domainClient(cls, id, name, file, start, end)
select id, name, "DomainClient", "ddd", file, start, end,
  "clean_engineering:OoadClass:" + file + ":" + name, "true", "implementation"
