/**
 * @name class-depends-on-classes
 * @kind problem
 * @id cdd/ce/edges/class-depends-on-classes
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"