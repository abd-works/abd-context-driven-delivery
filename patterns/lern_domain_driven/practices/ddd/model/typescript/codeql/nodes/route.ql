/**
 * @name lern routes
 * @kind problem
 * @id cdd/lern/ddd/route
 */

import javascript
import model

from File f, string id, string name, string file, int start, int end
where routeModule(f, id, name, file, start, end)
select id, name, "Route", "ddd", file, start, end, "implementation"
