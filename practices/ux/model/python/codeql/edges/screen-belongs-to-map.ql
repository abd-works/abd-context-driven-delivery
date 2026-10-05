/**
 * @name screen-belongs-to-map
 * @kind problem
 * @id cdd/ux/edges/screen-belongs-to-map
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
