import { fileURLToPath } from 'node:url'

import type { CddRoute } from '@cdd/cdd-shared'
import { epicRoutes } from '@cdd/practices/stories/model/epic'
import { scenarioRoutes } from '@cdd/practices/stories/model/scenario'
import { stepRoutes } from '@cdd/practices/stories/model/step'
import { storyRoutes } from '@cdd/practices/stories/model/story'
import { storyModelRoutes } from '@cdd/practices/stories/model/story-model'
import { fidelitySessionOutputRoutes } from '@cdd/space/session/fidelity-session-output'

// What a server mounts to serve the Story UI editor: the generated routes of the story map's objects and of the
// formats chosen for a fidelity, under STORY_MAP_API, and the built page, under STORY_MAP_PAGE. The editor keeps no
// routes, no store and no domain of its own: every edit is a story map tool.
export const storyMapRoutes: CddRoute[] = [...storyModelRoutes, ...epicRoutes, ...storyRoutes, ...scenarioRoutes, ...stepRoutes, ...fidelitySessionOutputRoutes]

// The page `npm run build` writes, which the server serves as static files, answering index.html for every other path.
export const storyMapBuild = fileURLToPath(new URL('./dist', import.meta.url))
