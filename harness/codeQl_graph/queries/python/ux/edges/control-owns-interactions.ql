/**
 * @name control-owns-interactions
 * @kind problem
 * @id cdd/ux/edges/control-owns-interactions
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
