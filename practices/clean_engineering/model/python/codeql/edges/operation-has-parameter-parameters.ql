/**
 * @name operation-has-parameter-parameters
 * @kind problem
 * @id cdd/ce/edges/operation-has-parameter-parameters
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"