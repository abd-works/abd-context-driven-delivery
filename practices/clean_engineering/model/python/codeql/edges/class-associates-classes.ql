/**
 * @name class-associates-classes
 * @kind problem
 * @id cdd/ce/edges/class-associates-classes
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"