/**
 * @name domain-concepts-not-technical-names
 * @kind problem
 * @id cdd/practice-graph/domain-concepts-not-technical-names
 * @problem.severity warning
 *
 * CodeQL emits the class name. Python WordNet decides agent nouns; leftover
 * technical suffixes stay in Python.
 */

import python
import subject_filter
import model

from Class cls
where inSubject(cls)
select cls, cls.getName(), cls
