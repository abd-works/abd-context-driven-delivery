/**
 * @name repo-owns-maps
 * @kind problem
 * @id cdd/ux/edges/repo-owns-maps
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
