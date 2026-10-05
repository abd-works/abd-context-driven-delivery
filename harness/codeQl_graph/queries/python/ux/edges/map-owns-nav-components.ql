/**
 * @name map-owns-nav-components
 * @kind problem
 * @id cdd/ux/edges/map-owns-nav-components
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
