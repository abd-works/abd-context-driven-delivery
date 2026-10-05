/**
 * @name context-belongs-to-map
 * @kind problem
 * @id cdd/ux/edges/context-belongs-to-map
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
