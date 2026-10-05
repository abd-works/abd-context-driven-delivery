/**
 * @name interaction-belongs-to-control
 * @kind problem
 * @id cdd/ux/edges/interaction-belongs-to-control
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
