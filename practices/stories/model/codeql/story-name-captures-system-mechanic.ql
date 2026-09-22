/**
 * @name story-name-captures-system-mechanic
 * @kind problem
 * @id cdd/practice-graph/story-name-captures-system-mechanic
 * @problem.severity warning
 *
 * CodeQL emits the story label. Python WordNet decides whether the verb is a
 * vague doer word over a generic noun.
 */

import javascript
import subject_filter
import model

from CallExpr call, string label
where inSubject(call) and storyLabel(call, label)
select call, label, call
