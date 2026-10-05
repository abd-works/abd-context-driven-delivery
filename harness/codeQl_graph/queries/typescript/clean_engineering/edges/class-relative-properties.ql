/**
 * @name class-relative-properties
 * @kind problem
 * @id cdd/ce/edges/class-relative-properties
 */

import javascript
import clean_engineering.ce

from string className, string name, string base, int start, string path, int end, string hint
where classProperty(className, name, base, start, path, end, hint) and isRelativeHint(hint)
select namedClassId(className), propertyId(path, name, className), "relative", 1, "direct"
