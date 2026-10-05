/**
 * @name example-retrieved-using-properties
 * @kind problem
 * @id cdd/stories/edges/example-retrieved-using-properties
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
