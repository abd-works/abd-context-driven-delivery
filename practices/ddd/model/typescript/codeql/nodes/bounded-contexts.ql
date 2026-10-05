/**
 * @name ddd bounded contexts
 * @kind problem
 * @id cdd/ddd/bounded-contexts
 */

import javascript
import ddd

from string id, string name, string file
where
  implicitContext() and
  id = dddNodeId("BoundedContext", ".", "bounded context") and
  name = "bounded context" and
  file = "."
  or
  contextPath(file, name) and id = dddNodeId("BoundedContext", file, name)
select id, name, "BoundedContext", "ddd", file, 1, 1, "discovery"
