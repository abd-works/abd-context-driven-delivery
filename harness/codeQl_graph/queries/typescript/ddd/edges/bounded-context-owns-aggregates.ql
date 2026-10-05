/**
 * @name bounded-context-owns-aggregates
 * @kind problem
 * @id cdd/ddd/edges/bounded-context-owns-aggregates
 */

import javascript
import ddd.ddd

from string parent, string child, string mod
where parent = boundedContextId() and aggregateFolder(mod) and child = aggregateId(mod)
select parent, child, "owns", 2, "direct" order by parent, child
