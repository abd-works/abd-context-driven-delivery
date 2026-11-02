/**
 * The server-side {Object}. The adapter holds its tools; this adds only what generation cannot know.
 *
 * ```
 * file: src/{context}/{object}/{object}-node.ts
 * ```
 */
import type { Request } from 'express'
import { z } from 'zod'

import { {Object}Tools } from '@cdd/{source-folders}/{object}'

import type { CddConnectionNode } from '../../cdd/cdd-connection-node'

const {Object}Address = z.object({ {object}: z.string().min(1) })

export class {Object}Node extends {Object}Tools {
  static fromRequest(cdd: CddConnectionNode, request: Request): {Object}Node {
    return new {Object}Node(cdd, {Object}Address.parse(request.params).{object})
  }
}
