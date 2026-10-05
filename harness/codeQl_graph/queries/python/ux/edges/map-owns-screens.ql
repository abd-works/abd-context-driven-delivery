/**
 * @name map-owns-screens
 * @kind problem
 * @id cdd/ux/edges/map-owns-screens
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
