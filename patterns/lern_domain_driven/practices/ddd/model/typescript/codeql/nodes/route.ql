/**
 * @name routes
 * @kind problem
 * @id cdd/lern/ddd/nodes/route
 */

import javascript
import lern

from File file, string slug
where routeFile(file, slug)
select routeId(file), routeName(slug), "Route", "ddd", fileSlash(file.getRelativePath()), 1, 1, "implementation"
