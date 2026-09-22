/**
 * @name no-orphaned-objects
 * @kind problem
 * @id cdd/practice-graph/no-orphaned-objects
 * @problem.severity warning
 *
 * Connector: the class is in the subject; relationships are searched on the whole database.
 */

import python
import subject_filter
import model

from Class cls
where orphanClass(cls)
select cls, "Class '" + cls.getName() + "' has no relationship to another type.", cls
