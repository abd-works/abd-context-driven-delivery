/**
 * @name domain-concepts-not-technical-names
 * @practice ddd
 * @fidelity bounded_context
 * @node class
 * @id ddd/bounded_context/domain-concepts-not-technical-names
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
