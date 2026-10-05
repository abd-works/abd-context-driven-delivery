/**
 * @name repo-owns-modules
 * @kind problem
 * @id cdd/ce/edges/repo-owns-modules
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
