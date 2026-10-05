/**
 * @name map-owns-transitions
 * @kind problem
 * @id cdd/ux/edges/map-owns-transitions
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
