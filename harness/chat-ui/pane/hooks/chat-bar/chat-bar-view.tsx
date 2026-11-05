// Model shell for the chat bar's views: plain functions that paint a client and hand presses to its actions.
import type { EngineInterface } from 'claude-code'

import type { ChatBarClient } from './chat-bar-client'
import type { FidelityClient } from './fidelity-client'
import type { StageClient } from './stage-client'

// ServerHealthBandView (reused), session name, FidelityView per dot, action button and picker, StageView per stage,
// handoff, files, close. Sized to bodyColumns.
export function ChatBarView($: EngineInterface, chatBar: ChatBarClient) { return null }

// One dot in its practice colour, shaded by status, violation count in red. Press: selectFidelity; second press: openBoard.
export function FidelityView($: EngineInterface, fidelity: FidelityClient) { return null }

// One stage icon, faint until reached, outlined while in progress. Press: selectStage.
export function StageView($: EngineInterface, stage: StageClient) { return null }
