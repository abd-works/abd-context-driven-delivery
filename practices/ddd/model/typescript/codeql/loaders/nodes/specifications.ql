/**
 * @name ddd specifications
 * @kind problem
 * @id cdd/ddd/specifications
 */

import javascript
import ddd

from ClassDefinition cls, string id, string name, string file, int start, int end
where dddClass(cls, "Specification", id, name, file, start, end)
select id, name, "Specification", "ddd", file, start, end,
  "clean_engineering:OoadClass:" + file + ":" + name
