/**
 * @name node-hosts-entity
 * @kind problem
 * @id cdd/lern/ddd/edges/node-hosts-entity
 */

import javascript
import model

from string parent, string child
where nodeHostsEntityEdge(parent, child)
select parent, child, "hosts", 5, "relationship"
