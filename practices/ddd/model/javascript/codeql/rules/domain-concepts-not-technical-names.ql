/**
 * @name domain-concepts-not-technical-names
 * @practice ddd
 * @fidelity bounded_context
 * @node class
 * @id ddd/bounded_context/domain-concepts-not-technical-names
 * CodeQL emits the class name. Python WordNet decides agent nouns; leftover
 * technical suffixes stay in Python.
 */

import javascript
import subject_filter
import model

from ClassDefinition cls
where inSubject(cls)
select cls, cls.getName(), cls
