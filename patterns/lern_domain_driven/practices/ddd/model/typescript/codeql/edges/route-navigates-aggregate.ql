/**
 * @name route-navigates-aggregate
 * @kind problem
 * @id cdd/lern/ddd/edges/route-navigates-aggregate
 */

import javascript
import lern

from File file, string slug
where routeFile(file, slug)
select routeId(file), aggregateId(slug), "navigates", 5, "relationship"
