/**
 * @name kebab-case-paths
 * @practice stories
 * @fidelity story_map
 * @node stories
 * @id stories/story_map/kebab-case-paths
 */

import python
import subject_filter
import model

from File file
where kebabPath(file)
select file, "Story file path is not kebab-case: " + file.getRelativePath(), file
