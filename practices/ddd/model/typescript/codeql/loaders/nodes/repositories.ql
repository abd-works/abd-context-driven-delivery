/**
 * @name ddd repositories
 * @kind problem
 * @id cdd/ddd/repositories
 */

import javascript
import ddd

from ClassDefinition cls, string id, string name, string file, int start, int end
where dddClass(cls, "Repository", id, name, file, start, end)
select id, name, "Repository", "ddd", file, start, end,
  "clean_engineering:OoadClass:" + file + ":" + name
