import { PythonCall } from '../python-call';
import type { InventoryBundle } from '../filter/FilterClient';

export class GraphClient {
  constructor(private readonly python = new PythonCall()) {}

  chooseFolder(): Promise<string> {
    return this.python.run('choose_folder');
  }

  chooseOverlayFolder(): Promise<string> {
    return this.python.run('choose_overlay_folder');
  }

  load(folder: string, practices: Record<string, string>, overlays?: string[], force = false): Promise<string> {
    const body: Record<string, unknown> = {
      folder,
      practices,
      database: folder,
      overlays: overlays ?? [],
    };
    if (force) {
      body.force = true;
    }
    return this.python.run('load_working_copy', body);
  }

  inventory(): Promise<InventoryBundle> {
    return this.python.run('inventory');
  }
}
