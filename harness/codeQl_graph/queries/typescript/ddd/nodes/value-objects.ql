/**
 * @name ddd value objects
 * @kind problem
 * @id cdd/ddd/value-objects
 */

import javascript
import ddd.ddd

from ClassDefinition cls, string id, string name, string file, int start, int end
where dddClass(cls, "ValueObject", id, name, file, start, end)
select id, name, "ValueObject", "ddd", file, start, end,
  "clean_engineering:OoadClass:" + file + ":" + name, "implementation"
