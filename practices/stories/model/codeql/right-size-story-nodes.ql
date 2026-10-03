/**
 * @name right-size-story-nodes
 * @practice stories
 * @fidelity story_map
 * @node stories
 * @id stories/story_map/right-size-story-nodes
 * @problem.severity warning
 */

import python
import model

from File file, string left, string right
where siblingStories(left, right, file) and similarSiblingNames(left, right)
select file,
  "Sibling stories '" + left + "' and '" + right + "' differ by at most two characters.",
  file
