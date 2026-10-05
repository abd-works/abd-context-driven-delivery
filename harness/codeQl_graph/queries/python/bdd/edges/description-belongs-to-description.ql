/**
 * @name description-belongs-to-description
 * @kind problem
 * @id cdd/bdd/edges/description-belongs-to-description
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
