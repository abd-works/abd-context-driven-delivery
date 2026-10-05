/**
 * @name operation-invokes-operations
 * @kind problem
 * @id cdd/ce/edges/operation-invokes-operations
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"