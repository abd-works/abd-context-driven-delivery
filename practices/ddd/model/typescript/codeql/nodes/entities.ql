/**
 * @name ddd entities
 * @kind problem
 * @id cdd/ddd/entities
 */

import javascript
import ddd

from ClassDefinition cls, string id, string name, string file, int start, int end
where dddClass(cls, "Entity", id, name, file, start, end)
select id, name, "Entity", "ddd", file, start, end,
  "clean_engineering:OoadClass:" + file + ":" + name, "false", "implementation"
