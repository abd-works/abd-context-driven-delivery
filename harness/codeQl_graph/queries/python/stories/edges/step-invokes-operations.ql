/**
 * @name step-invokes-operations
 * @kind problem
 * @id cdd/stories/edges/step-invokes-operations
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
