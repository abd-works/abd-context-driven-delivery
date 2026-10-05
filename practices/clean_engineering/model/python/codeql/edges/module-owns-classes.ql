/**
 * @name module-owns-classes
 * @kind problem
 * @id cdd/ce/edges/module-owns-classes
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"