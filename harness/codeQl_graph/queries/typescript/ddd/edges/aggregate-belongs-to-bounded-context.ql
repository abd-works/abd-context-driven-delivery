/**
 * @name aggregate-belongs-to-bounded-context
 * @kind problem
 * @id cdd/ddd/edges/aggregate-belongs-to-bounded-context
 */

import javascript
import ddd.ddd

from string parent, string child, string mod
where child = boundedContextId() and aggregateFolder(mod) and parent = aggregateId(mod)
select parent, child, "belongsTo", 4, "relationship"
