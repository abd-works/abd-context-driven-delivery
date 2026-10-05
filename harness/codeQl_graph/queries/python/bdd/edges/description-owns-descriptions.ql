/**
 * @name description-owns-descriptions
 * @kind problem
 * @id cdd/bdd/edges/description-owns-descriptions
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
