/**
 * @name transition-belongs-to-map
 * @kind problem
 * @id cdd/ux/edges/transition-belongs-to-map
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
