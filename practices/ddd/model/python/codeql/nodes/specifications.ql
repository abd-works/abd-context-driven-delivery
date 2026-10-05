/**
 * @name specifications
 * @kind problem
 * @id cdd/ddd/nodes/specifications
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "Module", "ddd", m.getFile().getShortName(), 1, 1, "discovery"
