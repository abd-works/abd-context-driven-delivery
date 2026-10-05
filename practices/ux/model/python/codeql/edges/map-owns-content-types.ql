/**
 * @name map-owns-content-types
 * @kind problem
 * @id cdd/ux/edges/map-owns-content-types
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
