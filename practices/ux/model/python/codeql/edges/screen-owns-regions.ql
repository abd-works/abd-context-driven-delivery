/**
 * @name screen-owns-regions
 * @kind problem
 * @id cdd/ux/edges/screen-owns-regions
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
