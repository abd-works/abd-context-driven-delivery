/**
 * What only the page knows about one {object}. A person acts on this class; each operation calls up to the generated
 * client, which posts to the {object}'s route, then brings the other page clients up to date. It adds no call, route,
 * or parsing of its own.
 *
 * ```
 * file: src/{context}/{object}/{object}-client.tsx
 * ```
 */
import { {Object}ClientGenerated, type {Object}Data } from '@cdd/{source folders}/{object}'

import type { {Page} } from '../{page}/{page}'

export class {Object}Client extends {Object}ClientGenerated {
  constructor(
    data: {Object}Data,
    private readonly page: {Page},
  ) {
    super(page.api, data)
  }

  override async {operation}(): Promise<this | null> {
    const changed = await super.{operation}()
    if (changed) await this.page.{refresh}()
    return changed
  }
}
