/**
 * @name region-owns-controls
 * @kind problem
 * @id cdd/ux/edges/region-owns-controls
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
