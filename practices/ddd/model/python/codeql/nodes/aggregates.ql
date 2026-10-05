/**
 * @name aggregates
 * @kind problem
 * @id cdd/ddd/nodes/aggregates
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "Module", "ddd", m.getFile().getShortName(), 1, 1, "discovery"
