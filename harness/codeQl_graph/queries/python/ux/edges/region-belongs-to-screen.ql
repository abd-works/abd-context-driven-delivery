/**
 * @name region-belongs-to-screen
 * @kind problem
 * @id cdd/ux/edges/region-belongs-to-screen
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
