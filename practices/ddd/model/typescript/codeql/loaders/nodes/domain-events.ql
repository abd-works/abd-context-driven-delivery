/**
 * @name ddd domain events
 * @kind problem
 * @id cdd/ddd/domain-events
 */

import javascript
import ddd

from ClassDefinition cls, string id, string name, string file, int start, int end
where dddClass(cls, "DomainEvent", id, name, file, start, end)
select id, name, "DomainEvent", "ddd", file, start, end,
  "clean_engineering:OoadClass:" + file + ":" + name
