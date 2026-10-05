/**
 * @name ddd domain services
 * @kind problem
 * @id cdd/ddd/domain-services
 */

import javascript
import ddd

from ClassDefinition cls, string id, string name, string file, int start, int end
where dddClass(cls, "DomainService", id, name, file, start, end)
select id, name, "DomainService", "ddd", file, start, end,
  "clean_engineering:OoadClass:" + file + ":" + name
