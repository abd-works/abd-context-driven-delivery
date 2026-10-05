import { PythonCall } from '../python-call';
import type { PracticeInventory } from '../filter/FilterClient';

export class GraphClient {
  constructor(private readonly python = new PythonCall()) {}

  chooseFolder(): Promise<string> {
    return this.python.run('choose_folder');
  }

  load(folder: string, practices: Record<string, string>): Promise<string> {
    return this.python.run('load_working_copy', { folder, practices, database: folder });
  }

  inventory(): Promise<Record<string, PracticeInventory>> {
    return this.python.run('inventory');
  }
}
