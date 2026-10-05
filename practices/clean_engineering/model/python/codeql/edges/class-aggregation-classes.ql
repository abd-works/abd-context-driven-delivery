/**
 * @name class-aggregation-classes
 * @kind problem
 * @id cdd/ce/edges/class-aggregation-classes
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"