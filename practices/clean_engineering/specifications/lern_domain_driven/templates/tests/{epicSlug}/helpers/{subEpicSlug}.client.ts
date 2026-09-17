/**
 * {{subEpicSlug}}.client.ts — Client tier helper.
 *
 * vi.mock at API boundary; Testing Library for React assertions.
 */
import { {{SubEpicName}}BaseHelper } from './{{subEpicSlug}}.base';

export class {{SubEpicName}}ClientHelper extends {{SubEpicName}}BaseHelper {
  protected async seed(): Promise<void> {
    // Mock API responses
  }

  async cleanup(): Promise<void> {
    // Clear mocks
  }
}
