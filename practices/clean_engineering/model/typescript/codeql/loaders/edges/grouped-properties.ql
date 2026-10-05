/**
 * @name grouped-properties
 * @kind problem
 * @id cdd/ce/edges/grouped-properties
 */

import javascript
import ce

from string className, string name, string base, int start, string path, int end, string hint
where classProperty(className, name, base, start, path, end, hint) and not isRelativeHint(hint)
select namedClassId(className), propertyId(path, name, className), "properties", 3, "grouped"
