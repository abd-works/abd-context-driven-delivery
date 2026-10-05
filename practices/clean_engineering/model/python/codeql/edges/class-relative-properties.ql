/**
 * @name class-relative-properties
 * @kind problem
 * @id cdd/ce/edges/class-relative-properties
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"