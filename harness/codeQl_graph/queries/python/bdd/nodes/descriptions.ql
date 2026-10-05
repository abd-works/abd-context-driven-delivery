/**
 * @name descriptions
 * @kind problem
 * @id cdd/bdd/nodes/descriptions
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "Module", "bdd", m.getFile().getShortName(), 1, 1, "discovery"
