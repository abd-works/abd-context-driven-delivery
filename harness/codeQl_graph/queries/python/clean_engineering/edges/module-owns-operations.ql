/**
 * @name module-owns-operations
 * @kind problem
 * @id cdd/clean_engineering/edges/module-owns-operations
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
