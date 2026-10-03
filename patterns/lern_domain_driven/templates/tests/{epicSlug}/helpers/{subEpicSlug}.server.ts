/**
 * {{subEpicSlug}}.server.ts — Server tier helper.
 *
 * Seeds DB, uses Supertest for HTTP assertions.
 */
import { {{SubEpicName}}BaseHelper } from './{{subEpicSlug}}.base';

export class {{SubEpicName}}ServerHelper extends {{SubEpicName}}BaseHelper {
  protected async seed(): Promise<void> {
    // Insert test aggregate roots into the lowdb Memory adapter
  }

  async cleanup(): Promise<void> {
    // Clear test data
  }
}
