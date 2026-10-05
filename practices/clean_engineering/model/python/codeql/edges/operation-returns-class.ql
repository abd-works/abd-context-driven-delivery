/**
 * @name operation-returns-class
 * @kind problem
 * @id cdd/ce/edges/operation-returns-class
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"