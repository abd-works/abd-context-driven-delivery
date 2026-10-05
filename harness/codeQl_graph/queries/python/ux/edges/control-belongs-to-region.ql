/**
 * @name control-belongs-to-region
 * @kind problem
 * @id cdd/ux/edges/control-belongs-to-region
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
