/**
 * @name operation-owns-parameters
 * @kind problem
 * @id cdd/ce/edges/operation-owns-parameters
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"