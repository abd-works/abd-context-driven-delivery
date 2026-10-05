/**
 * @name content-types
 * @kind problem
 * @id cdd/ux/nodes/content-types
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "Module", "ux", m.getFile().getShortName(), 1, 1, "discovery"
