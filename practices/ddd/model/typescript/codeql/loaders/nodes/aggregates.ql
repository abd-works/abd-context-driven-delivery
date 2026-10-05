/**
 * @name ddd aggregates
 * @kind problem
 * @id cdd/ddd/aggregates
 */

import javascript
import ddd

from string mod, string id, string file
where
  aggregateFolder(mod) and
  file = "src/" + mod and
  id = aggregateId(mod)
select id, mod, "Aggregate", "ddd", file, 1, 1, boundedContextId()
