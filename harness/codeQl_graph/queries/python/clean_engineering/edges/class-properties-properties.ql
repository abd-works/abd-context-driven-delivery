/**
 * @name class-properties-properties
 * @kind problem
 * @id cdd/ce/edges/class-properties-properties
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"