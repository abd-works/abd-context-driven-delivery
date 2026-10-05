/**
 * @name example-retrieved-using-operations
 * @kind problem
 * @id cdd/stories/edges/example-retrieved-using-operations
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
