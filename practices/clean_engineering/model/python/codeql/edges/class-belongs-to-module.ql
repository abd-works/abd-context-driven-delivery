/**
 * @name class-belongs-to-module
 * @kind problem
 * @id cdd/ce/edges/class-belongs-to-module
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"