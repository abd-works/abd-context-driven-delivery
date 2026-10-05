/**
 * @name ddd entity roots
 * @kind problem
 * @id cdd/ddd/entity-roots
 */

import javascript
import ddd

from ClassDefinition cls, string id, string name, string file, int start, int end
where dddClass(cls, "EntityRoot", id, name, file, start, end)
select id, name, "EntityRoot", "ddd", file, start, end,
  "clean_engineering:OoadClass:" + file + ":" + name, "true", "implementation"
