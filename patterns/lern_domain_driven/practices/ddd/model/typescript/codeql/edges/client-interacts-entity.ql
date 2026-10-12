/**
 * @name client-interacts-entity
 * @kind problem
 * @id cdd/lern/ddd/edges/client-interacts-entity
 */

import javascript
import model

from string parent, string child
where clientInteractsEntityEdge(parent, child)
select parent, child, "interacts", 5, "relationship"
