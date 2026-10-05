/**
 * @name uses
 * @kind problem
 * @id cdd/stories/edges/uses
 */

import javascript

from File f
where none()
select f.getRelativePath(), f.getRelativePath(), "uses", 9, "relationship"
