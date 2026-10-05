/**
 * @name factories
 * @kind problem
 * @id cdd/ddd/nodes/factories
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "Module", "ddd", m.getFile().getShortName(), 1, 1, "discovery"
