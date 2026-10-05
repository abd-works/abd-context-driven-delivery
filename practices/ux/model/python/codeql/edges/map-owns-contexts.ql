/**
 * @name map-owns-contexts
 * @kind problem
 * @id cdd/ux/edges/map-owns-contexts
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
