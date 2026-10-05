/**
 * @name ddd factories
 * @kind problem
 * @id cdd/ddd/factories
 */

import javascript
import ddd

from ClassDefinition cls, string id, string name, string file, int start, int end
where dddClass(cls, "Factory", id, name, file, start, end)
select id, name, "Factory", "ddd", file, start, end,
  "clean_engineering:OoadClass:" + file + ":" + name, "implementation"
