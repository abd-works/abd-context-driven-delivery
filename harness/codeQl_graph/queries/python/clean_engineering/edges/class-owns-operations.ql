/**
 * @name class-owns-operations
 * @kind problem
 * @id cdd/ce/edges/class-owns-operations
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"