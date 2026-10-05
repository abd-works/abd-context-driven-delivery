/**
 * @name epic-uses-modules
 * @kind problem
 * @id cdd/stories/edges/epic-uses-modules
 */

import javascript

from File f
where none()
select f.getRelativePath(), f.getRelativePath(), "uses", 9, "relationship"
